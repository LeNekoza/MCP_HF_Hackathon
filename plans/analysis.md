## Implementation Plan for Smart Hospital Coding Agent (Updated)

> **Scope:** Integrate all operational & predictive analyses into the existing Gradio dashboard, leveraging the current interactive graph component by making its data dynamic and driven by a new *Analysis* selector, with client-side caching for improved performance.

---

## 0 Reference Material

| Resource                                                                 | Purpose                                                                                                                     |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `hospital_analysis_latest.ipynb` (path:`hospital_analysis_latest.ipynb`) | Contains data-wrangling & modeling snippets for each insight. Import functions directly or copy logic into backend helpers. |

---

## 1 High-Level Milestones

1. **Refactor notebook logic into reusable Python modules**
2. **Create analysis API endpoints / helper functions** (one per insight)
3. **Expose a unified **\`\`** endpoint** for all insights
4. **Enhance the dashboard UI**:

   * Add *Analysis* dropdown selector
   * Update *Chart-Type* dropdown dynamically
   * Drive the existing interactive graph component with fetched data
5. **Implement client-side caching** of analysis results in local storage
6. **Map each analysis to default & extra chart types**
7. **Wire chart component reactivity** (state → fetch data → redraw)
8. **Testing & polishing**

---

## 2 Data & Model Refactor (Backend)

| File / Module                          | Task                                                                 |
| -------------------------------------- | -------------------------------------------------------------------- |
| `backend/analytics/occupancy.py`       | `get_bed_snapshot(date)` – JSON of ward-level occupancy & capacity   |
| `backend/analytics/census_forecast.py` | `forecast_bed_census(days=3)` – Holt-Winters forecast                |
| `backend/analytics/admission_split.py` | `admission_split(days_back=14)` – elective vs emergency counts       |
| `backend/analytics/los_model.py`       | `LOSPredictor.predict(features)` + `los_summary()` for ward averages |
| `backend/analytics/burn_rate.py`       | `forecast_consumables(days=7)` – consumable usage forecast           |
| `backend/analytics/staffing.py`        | `forecast_staff(days=3)` – staffing requirement forecast             |

> **Tip:** Copy cells from the notebook; wrap into pure functions; store fitted models (pickled) under `models/`.

---

## 3 Unified Analysis Registry

Create `backend/analysis_registry.py`:

```python
ANALYSES = {
    "bed_snapshot": {
        "label": "Real-time bed-​occupancy by ward",
        "fn": analytics.occupancy.get_bed_snapshot,
        "default_chart": "stacked_bar",
        "extra_charts": ["100pct_area"],
    },
    "census_forecast": {
        "label": "Short-horizon bed census",
        "fn": analytics.census_forecast.forecast_bed_census,
        "default_chart": "line",
        "extra_charts": ["line_conf_band"],
    },
    "admission_split": {
        "label": "Elective vs emergency demand split",
        "fn": analytics.admission_split.admission_split,
        "default_chart": "stacked_bar",
        "extra_charts": ["pie"],
    },
    "los_prediction": {
        "label": "Average length-of-stay prediction",
        "fn": analytics.los_model.los_summary,
        "default_chart": "bar_h",
        "extra_charts": ["box"],
    },
    "burn_rate": {
        "label": "Consumable burn-rate forecast",
        "fn": analytics.burn_rate.forecast_consumables,
        "default_chart": "stacked_area",
        "extra_charts": [],
    },
    "staffing": {
        "label": "Staffing needs",
        "fn": analytics.staffing.forecast_staff,
        "default_chart": "grouped_bar",
        "extra_charts": ["dual_axis_line"],
    },
}
```

**Endpoint** (`FastAPI` or Gradio `@predict`):

```python
@post("/get_analysis")
async def get_analysis(analysis_id: str):
    item = ANALYSES[analysis_id]
    data = item["fn"]()
    return {
        "default_chart": item["default_chart"],
        "extra_charts": item["extra_charts"],
        "data": data,
    }
```

---

## 4 UI Changes (Gradio Blocks)

1. **Reuse existing interactive graph component**—no new chart renderers; only data & type controls change.
2. **Add** `gr.Dropdown` **for Analysis** above the graph:

   ```python
   analysis_selector = gr.Dropdown(
       choices=[(v["label"], k) for k, v in ANALYSES.items()],
       value="bed_snapshot",
       label="Select Analysis",
   )
   ```
3. **Extend** `chart_type_selector` **choices** dynamically:

   * On **Analysis** change, check local storage cache.

     1. If cached data exists for `analysis_id`, load from local storage and render immediately.
     2. Otherwise, call `/get_analysis`.
   * After fetching, update cache: `localStorage.setItem(analysis_id, JSON.stringify(payload.data))`.
   * Update graph’s data source.
   * Update `chart_type_selector.choices = ["line","bar","scatter","pie"] + extra_charts`.
   * Set `chart_type_selector.value = default_chart`.
4. **Add Refresh Button** to the right of the *Analysis* dropdown:

   ```python
   refresh_btn = gr.Button(value="⟳ Refresh Data")
   ```

   * On click, clear storage for the selected `analysis_id`, re-fetch via `/get_analysis`, update cache & re-render.
5. **Graph component** remains single `<Plot/>` driven by reactive state `{ chart_type, data }`.
6. **Error handling**: if user picks a chart-type not supported (not in payload), show toast: "Chart unavailable for this analysis".

---

## 5 End-to-End Flow

```
HoD selects analysis →
   • If cache hit: load data from localStorage → render graph & chart-type dropdown
   • If cache miss: call /get_analysis → cache data → render graph & chart-type dropdown

User clicks “Refresh”: clear cache for analysis_id → call /get_analysis → update cache → re-render
```
