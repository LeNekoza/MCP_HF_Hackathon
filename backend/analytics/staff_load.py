"""
Staff load analytics
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any
from ..database import get_occupancy, get_users
from ..storage import save_analysis_result, save_model_data


def staff_load_analysis(top_n: int = 10, save_results: bool = True) -> Dict[str, Any]:
    """
    Analyze staff workload based on patient assignments

    Args:
        top_n: Number of top staff members to return
        save_results: Whether to save results to storage

    Returns:
        JSON-serializable dict with staff load data
    """
    # Load data
    occupancy = get_occupancy()
    users = get_users()

    # Clean data
    for df in (occupancy, users):
        df.drop(
            columns=[c for c in df.columns if c.startswith("Unnamed")],
            inplace=True,
            errors="ignore",
        )

    # Check if attendee data is available
    if "attendee" not in occupancy.columns:
        # Generate mock staff assignments if not available
        return _generate_mock_staff_load(users, top_n, save_results)

    # Process actual staff assignments
    # Filter to active patients only
    current_time = pd.Timestamp.utcnow().tz_localize(None)

    # Ensure discharged_at is timezone-naive for comparison
    occupancy_copy = occupancy.copy()
    if "discharged_at" in occupancy_copy.columns:
        occupancy_copy["discharged_at"] = pd.to_datetime(
            occupancy_copy["discharged_at"]
        ).dt.tz_localize(None)

    active_patients = occupancy_copy[
        (occupancy_copy["discharged_at"].isna())
        | (occupancy_copy["discharged_at"] > current_time)
    ].copy()

    # Handle staff assignments (can be semicolon-separated list)
    staff_assignments = []
    for _, row in active_patients.iterrows():
        if pd.notnull(row["attendee"]):
            # Split multiple attendees if semicolon-separated
            attendees = str(row["attendee"]).split(";")
            for attendee in attendees:
                attendee = attendee.strip()
                if attendee:
                    staff_assignments.append(
                        {
                            "staff_id": attendee,
                            "patient_id": row.get(
                                "patient_id", row.get("id", "unknown")
                            ),
                            "room_id": row.get("room_id", "unknown"),
                        }
                    )

    # Convert to DataFrame for analysis
    assignments_df = pd.DataFrame(staff_assignments)

    if len(assignments_df) == 0:
        return _generate_mock_staff_load(users, top_n, save_results)

    # Count patient assignments per staff member
    staff_load = (
        assignments_df.groupby("staff_id")
        .size()
        .reset_index(name="patient_assignments")
    )

    # Merge with user data for full names and roles
    staff_load = staff_load.merge(
        users[["id", "full_name", "staff_type"]],
        left_on="staff_id",
        right_on="id",
        how="left",
    )

    # Fill missing data
    staff_load["full_name"] = staff_load["full_name"].fillna("Unknown Staff")
    staff_load["staff_type"] = staff_load["staff_type"].fillna("Unknown")

    # Sort by workload and get top N
    top_staff = staff_load.sort_values("patient_assignments", ascending=False).head(
        top_n
    )

    # Prepare staff data
    staff_data = []
    total_assignments = staff_load["patient_assignments"].sum()
    for _, staff in top_staff.iterrows():
        assignments = int(staff["patient_assignments"])
        assignment_percentage = (
            round((assignments / total_assignments) * 100)
            if total_assignments > 0
            else 0
        )
        staff_data.append(
            {
                "staff_id": staff["staff_id"],
                "full_name": staff["full_name"],
                "staff_type": staff["staff_type"],
                "patient_assignments": assignments,
                "workload_level": _get_workload_level(assignments, staff["staff_type"]),
                "assignment_percentage": assignment_percentage,
            }
        )

    # Calculate summary statistics
    summary_stats = {
        "total_active_staff": len(staff_load),
        "total_patient_assignments": int(staff_load["patient_assignments"].sum()),
        "avg_assignments_per_staff": float(
            staff_load["patient_assignments"].mean().round(1)
        ),
        "max_assignments": int(staff_load["patient_assignments"].max()),
        "min_assignments": int(staff_load["patient_assignments"].min()),
        "std_assignments": float(staff_load["patient_assignments"].std().round(2)),
    }

    # Workload distribution by staff type
    workload_by_type = []
    for staff_type in staff_load["staff_type"].unique():
        type_data = staff_load[staff_load["staff_type"] == staff_type]
        workload_by_type.append(
            {
                "staff_type": staff_type,
                "staff_count": len(type_data),
                "total_assignments": int(type_data["patient_assignments"].sum()),
                "avg_assignments": float(
                    type_data["patient_assignments"].mean().round(1)
                ),
                "max_assignments": int(type_data["patient_assignments"].max()),
                "min_assignments": int(type_data["patient_assignments"].min()),
            }
        )

    # Workload alerts
    alerts = _generate_workload_alerts(staff_load)

    result = {
        "top_staff": staff_data,
        "summary_statistics": summary_stats,
        "workload_by_type": workload_by_type,
        "alerts": alerts,
        "analysis_timestamp": datetime.now().isoformat(),
    }

    # Save results and model data if requested
    if save_results:
        # Save the result data (JSON)
        save_analysis_result("staff_load", result)

        # Force CSV generation
        save_analysis_result("staff_load", result, format="csv")

        # Save model/analysis data
        model_data = {
            "analysis_type": "staff_load",
            "top_n_analyzed": top_n,
            "workload_calculation": "count of current patient assignments",
            "workload_thresholds": {
                "nurse": {"normal": "1-4", "high": "5-7", "critical": "8+"},
                "doctor": {"normal": "1-8", "high": "9-12", "critical": "13+"},
                "default": {"normal": "1-5", "high": "6-8", "critical": "9+"},
            },
            "data_quality": {
                "total_staff_analyzed": len(staff_load),
                "has_attendee_data": "attendee" in occupancy.columns,
                "active_assignments": summary_stats["total_patient_assignments"],
                "data_completeness": float(
                    staff_load["full_name"].notna().mean().round(2)
                ),
            },
            "insights": summary_stats,
        }
        save_model_data("staff_load", model_data)

    return result


def _generate_mock_staff_load(
    users: pd.DataFrame, top_n: int, save_results: bool
) -> Dict[str, Any]:
    """Generate mock staff load data when attendee data is not available"""
    import numpy as np

    # Create mock assignments
    users_sample = users.head(min(50, len(users))).copy()
    users_sample["patient_assignments"] = np.random.poisson(
        lam=3, size=len(users_sample)
    )
    users_sample["patient_assignments"] = users_sample["patient_assignments"].clip(
        0, 12
    )

    # Get top N
    top_staff = users_sample.sort_values("patient_assignments", ascending=False).head(
        top_n
    )

    # Prepare staff data
    staff_data = []
    total_assignments = users_sample["patient_assignments"].sum()
    for _, staff in top_staff.iterrows():
        staff_type = staff.get("staff_type", "Unknown")
        assignments = int(staff["patient_assignments"])
        assignment_percentage = (
            round((assignments / total_assignments) * 100)
            if total_assignments > 0
            else 0
        )
        staff_data.append(
            {
                "staff_id": staff.get("id", "unknown"),
                "full_name": staff.get("full_name", "Unknown Staff"),
                "staff_type": staff_type,
                "patient_assignments": assignments,
                "workload_level": _get_workload_level(assignments, staff_type),
                "assignment_percentage": assignment_percentage,
            }
        )

    summary_stats = {
        "total_active_staff": len(users_sample),
        "total_patient_assignments": int(users_sample["patient_assignments"].sum()),
        "avg_assignments_per_staff": float(
            users_sample["patient_assignments"].mean().round(1)
        ),
        "max_assignments": int(users_sample["patient_assignments"].max()),
        "min_assignments": int(users_sample["patient_assignments"].min()),
        "std_assignments": float(users_sample["patient_assignments"].std().round(2)),
    }

    result = {
        "top_staff": staff_data,
        "summary_statistics": summary_stats,
        "workload_by_type": [],
        "alerts": [
            {
                "level": "info",
                "message": "Mock data generated - attendee information not available",
            }
        ],
        "is_mock_data": True,
        "analysis_timestamp": datetime.now().isoformat(),
    }

    if save_results:
        save_analysis_result("staff_load", result)
        save_model_data(
            "staff_load",
            {"analysis_type": "staff_load", "data_source": "mock_generated"},
        )

    return result


def _get_workload_level(assignments: int, staff_type: str) -> str:
    """Determine workload level based on assignments and staff type"""
    staff_type = (staff_type or "").lower()

    if "nurse" in staff_type:
        if assignments <= 4:
            return "normal"
        elif assignments <= 7:
            return "high"
        else:
            return "critical"
    elif "doctor" in staff_type:
        if assignments <= 8:
            return "normal"
        elif assignments <= 12:
            return "high"
        else:
            return "critical"
    else:
        # Default thresholds
        if assignments <= 5:
            return "normal"
        elif assignments <= 8:
            return "high"
        else:
            return "critical"


def _generate_workload_alerts(staff_load: pd.DataFrame) -> list:
    """Generate alerts for staff workload issues"""
    alerts = []

    # High workload staff
    high_workload = staff_load[staff_load["patient_assignments"] > 8]
    if len(high_workload) > 0:
        alerts.append(
            {
                "level": "warning",
                "message": f"{len(high_workload)} staff members have high workloads (>8 patients)",
                "action": "Consider workload redistribution",
                "count": len(high_workload),
            }
        )

    # Critical workload staff
    critical_workload = staff_load[staff_load["patient_assignments"] > 12]
    if len(critical_workload) > 0:
        alerts.append(
            {
                "level": "critical",
                "message": f"{len(critical_workload)} staff members have critical workloads (>12 patients)",
                "action": "Immediate workload adjustment required",
                "count": len(critical_workload),
            }
        )

    # Uneven distribution
    if len(staff_load) > 0:
        std_dev = staff_load["patient_assignments"].std()
        if std_dev > 3:
            alerts.append(
                {
                    "level": "info",
                    "message": "Uneven workload distribution detected",
                    "action": "Review assignment policies",
                    "count": 0,
                }
            )

    if len(alerts) == 0:
        alerts.append(
            {
                "level": "info",
                "message": "Workload distribution appears balanced",
                "action": "Continue monitoring",
                "count": 0,
            }
        )

    return alerts
