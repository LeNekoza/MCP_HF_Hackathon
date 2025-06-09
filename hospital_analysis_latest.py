# -*- coding: utf-8 -*-
"""
Smart Hospital Assistant – End‑to‑End Analytics Script (v2)
===========================================================
Full, self‑contained analytics covering:
    • Zero‑ML operational snapshots
    • Short‑horizon forecasts
    • LOS model
    • Consumable & staffing projections
Fixes applied in **v2**
---------------------
✓ Safe handling of `pd.NaT` when building daily bed‑census series
✓ Explicit Agg matplotlib backend for headless servers
✓ Time‑zone stripping before `.dt.hour`
✓ Fallback tool‑utilisation calculation when `quantity_in_use` absent
✓ Nurse‑per‑bed ratio recomputed weekly; CLI override via `--nurse‑ratio` flag
✓ Dummy Poisson usage gated behind `--demo` flag to avoid accidental mis‑use
✓ Robust output folder creation with `parents=True`
✓ Small code clean‑ups & type hints

Run `python hospital_analysis.py --help` for CLI options.
"""
from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # headless friendly
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

warnings.filterwarnings("ignore", category=FutureWarning)
plt.rcParams["figure.autolayout"] = True

# ----------------------------------------------------------------------------
# CLI args
# ----------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Smart Hospital analytics runner")
parser.add_argument("--demo", action="store_true", help="Generate dummy consumable usage data")
parser.add_argument("--nurse-ratio", type=float, help="Override nurse-per-bed ratio")
ARGS = parser.parse_args()

# ----------------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------------
DATA_DIR: Path = Path(__file__).parent
OUT_DIR: Path = DATA_DIR / "outputs"
OUT_DIR.mkdir(exist_ok=True, parents=True)

def save_table(df: pd.DataFrame, name: str) -> None:
    path = OUT_DIR / f"{name}.csv"
    df.to_csv(path, index=False)
    print(f"\n===== {name} =====")
    print(df.head(15))

def save_plot(fig, name: str) -> None:
    fig.savefig(OUT_DIR / f"{name}.png", dpi=150)

# ----------------------------------------------------------------------------
# Load CSVs
# ----------------------------------------------------------------------------
print("Loading CSVs…")
rooms     = pd.read_csv(DATA_DIR / "rooms.csv")
occupancy = pd.read_csv(DATA_DIR / "occupancy.csv", parse_dates=["assigned_at", "discharged_at"], dayfirst=True)
patients  = pd.read_csv(DATA_DIR / "patient_records.csv", parse_dates=["date_of_birth"], dayfirst=True)
users     = pd.read_csv(DATA_DIR / "users.csv")
tools     = pd.read_csv(DATA_DIR / "tools.csv")
inv       = pd.read_csv(DATA_DIR / "hospital_inventory.csv", parse_dates=["expiry_date"], dayfirst=True)

for df in (rooms, occupancy, patients, users, tools, inv):
    df.drop(columns=[c for c in df if c.startswith("Unnamed")], inplace=True, errors="ignore")

# Strip TZ to avoid .dt.hour errors
auto_cols = ["assigned_at", "discharged_at"]
for col in auto_cols:
    occupancy[col] = occupancy[col].dt.tz_localize(None)

# ----------------------------------------------------------------------------
# 1 Bed Occupancy Snapshot
# ----------------------------------------------------------------------------
print("\n[1] Bed Occupancy by Ward…")
room_type_map = rooms.set_index("id")["room_type"]
active_now = occupancy[(occupancy["discharged_at"].isna()) | (occupancy["discharged_at"] > pd.Timestamp.utcnow())].copy()
active_now["room_type"] = active_now["room_id"].map(room_type_map)
occ_tbl = (
    active_now.groupby("room_type").size().rename("current_occupied_beds").to_frame()
    .join(rooms.groupby("room_type")["bed_capacity"].sum().rename("total_beds"))
    .fillna(0)
)
occ_tbl["utilisation_pct"] = (occ_tbl.current_occupied_beds / occ_tbl.total_beds * 100).round(1)
save_table(occ_tbl.reset_index(), "occupancy_by_ward")

# ----------------------------------------------------------------------------
# 2 Average LOS by ward
# ----------------------------------------------------------------------------
print("\n[2] Average LOS by Ward…")
los_df = occupancy.dropna(subset=["discharged_at"]).copy()
los_df["los_days"] = (los_df.discharged_at - los_df.assigned_at).dt.total_seconds() / 86400
los_df["room_type"] = los_df.room_id.map(room_type_map)
los_tbl = los_df.groupby("room_type")["los_days"].mean().round(2).reset_index(name="avg_los_days")
save_table(los_tbl, "average_los_by_ward")

# ----------------------------------------------------------------------------
# 3 Tool Utilisation top‑10
# ----------------------------------------------------------------------------
print("\n[3] Tool Utilisation…")
if "quantity_in_use" in tools:
    tools["util_pct"] = (tools.quantity_in_use / tools.quantity_available).clip(0,1)*100
else:
    tools["util_pct"] = ((tools.quantity_total - tools.quantity_available) / tools.quantity_total).clip(0,1)*100
util_top10 = tools.sort_values("util_pct", ascending=False).head(10)[["tool_name","util_pct"]].round(1)
save_table(util_top10, "tool_utilisation_top10")

# ----------------------------------------------------------------------------
# 4 Inventory Expiry ≤ 90 days
# ----------------------------------------------------------------------------
print("\n[4] Expiry Radar…")
inv["days_to_expiry"] = (inv.expiry_date - pd.Timestamp.utcnow()).dt.days
soon = inv[inv.days_to_expiry.le(90)].sort_values("days_to_expiry")[["item_name","days_to_expiry","quantity_available"]]
save_table(soon.head(20), "inventory_expiring_soon")

# ----------------------------------------------------------------------------
# 5 Staff Load top‑10
# ----------------------------------------------------------------------------
print("\n[5] Staff Load…")
if "attendee" in occupancy:
    tmp = occupancy.dropna(subset=["attendee"]).copy()
    tmp["attendee_list"] = tmp.attendee.str.split(";")
    tmp = tmp.explode("attendee_list")
    staff_tbl = (
        tmp.groupby("attendee_list").size().rename("patient_assignments").to_frame()
        .merge(users[["id","full_name","staff_type"]], left_on="attendee_list", right_on="id", how="left")
        .sort_values("patient_assignments", ascending=False).head(10)[["full_name","staff_type","patient_assignments"]]
    )
    save_table(staff_tbl, "staff_load_top10")
else:
    print("[attendee missing – skipped]")

# ----------------------------------------------------------------------------
# 6 3‑day Bed‑Census Forecast
# ----------------------------------------------------------------------------
print("\n[6] Bed‑Census Forecast…")
series_dates = []
for _, r in occupancy.iterrows():
    end_date = r.discharged_at if pd.notnull(r.discharged_at) else pd.Timestamp.utcnow()
    series_dates.append(pd.date_range(r.assigned_at.normalize(), end_date.normalize(), freq="D"))
series = pd.Series(pd.to_datetime(np.concatenate(series_dates))).value_counts().sort_index()
series = series.asfreq("D", fill_value=0)
fit = ExponentialSmoothing(series, initialization_method="estimated").fit()
fc = fit.forecast(3)
fc_df = fc.to_frame("predicted_occupied_beds").reset_index()
fc_df["util_pct"] = (fc_df.predicted_occupied_beds / rooms.bed_capacity.sum()*100).round(1)
save_table(fc_df, "bed_census_forecast")
# plot
fig = plt.figure(figsize=(8,4))
series.tail(30).plot(label="history")
fc.plot(style="--o", label="forecast")
plt.legend(); save_plot(fig, "bed_census_forecast")

# ----------------------------------------------------------------------------
# 7 Elective vs Emergency
# ----------------------------------------------------------------------------
print("\n[7] Elective vs Emergency…")
occupancy["admission_type"] = np.where(occupancy.assigned_at.dt.hour.between(8,17),"Elective","Emergency")
ratio = occupancy.admission_type.value_counts().to_frame("Count")
ratio["Percentage"] = (ratio.Count/ratio.Count.sum()*100).round(1)
save_table(ratio.reset_index(), "elective_emergency_overall")

daily = occupancy.groupby([occupancy.assigned_at.dt.date, "admission_type"]).size().unstack(fill_value=0).rename_axis("date").reset_index()
save_table(daily.tail(14), "elective_emergency_daily")

# ----------------------------------------------------------------------------
# 8 LOS Prediction Model
# ----------------------------------------------------------------------------
print("\n[8] LOS Prediction…")
los_df = los_df[los_df.los_days.between(0, 365)]  # sane bounds
los_df["age_at_adm"] = los_df.age_at_adm.clip(lower=0)
feat = ["admission_type","room_type","gender","age_at_adm"]
X,y = los_df[feat], los_df.los_days
pipe = Pipeline([("prep", ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), feat[:-1]),
