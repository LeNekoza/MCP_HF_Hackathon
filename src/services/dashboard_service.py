"""
Dashboard Service - Provides dynamic data for hospital dashboard metrics
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class DashboardService:
    """Service to generate and manage dashboard metrics data"""

    def __init__(self):
        self.last_update = time.time()
        self.base_metrics = {
            "icuOccupancy": 71,
            "staffAvailability": {"doctors": 75, "nurses": 60},
            "toolUsage": [60, 40, 70, 35, 85],
            "emergencyLoad": [70, 50, 45, 40, 35, 30, 25],
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get current dashboard metrics data

        Returns:
            Dictionary containing all dashboard metrics
        """
        current_time = time.time()

        # Update metrics with some realistic variation
        return {
            "icuOccupancy": self._get_icu_occupancy(),
            "staffAvailability": self._get_staff_availability(),
            "toolUsage": self._get_tool_usage(),
            "emergencyLoad": self._get_emergency_load(),
            "timestamp": current_time,
            "lastUpdate": datetime.now().isoformat(),
            "status": "operational",
            "alerts": self._get_current_alerts(),
            "quickStats": self._get_quick_stats(),
        }

    def _get_icu_occupancy(self) -> int:
        """Get ICU occupancy percentage with realistic fluctuation"""
        base = self.base_metrics["icuOccupancy"]
        # Slight random variation (-5 to +5)
        variation = random.randint(-5, 5)
        new_value = max(45, min(95, base + variation))

        # Update base for next call
        self.base_metrics["icuOccupancy"] = new_value
        return new_value

    def _get_staff_availability(self) -> Dict[str, int]:
        """Get staff availability with realistic patterns"""
        current_hour = datetime.now().hour

        # Doctors availability varies by time of day
        if 8 <= current_hour <= 18:  # Day shift
            doctors_base = 85
        elif 18 <= current_hour <= 23:  # Evening shift
            doctors_base = 70
        else:  # Night shift
            doctors_base = 60

        # Nurses follow similar but different patterns
        if 6 <= current_hour <= 14:  # Day shift
            nurses_base = 80
        elif 14 <= current_hour <= 22:  # Evening shift
            nurses_base = 75
        else:  # Night shift
            nurses_base = 65

        # Add some random variation
        doctors = max(40, min(95, doctors_base + random.randint(-10, 10)))
        nurses = max(35, min(90, nurses_base + random.randint(-15, 15)))

        return {"doctors": doctors, "nurses": nurses}

    def _get_tool_usage(self) -> List[int]:
        """Get tool usage statistics"""
        base_usage = self.base_metrics["toolUsage"]

        # Update each tool's usage with small variations
        new_usage = []
        for i, usage in enumerate(base_usage):
            variation = random.randint(-8, 12)  # Slight upward trend
            new_value = max(20, min(90, usage + variation))
            new_usage.append(new_value)

        # Update base for next call
        self.base_metrics["toolUsage"] = new_usage
        return new_usage

    def _get_emergency_load(self) -> List[int]:
        """Get emergency room load data (last 7 time periods)"""
        current_hour = datetime.now().hour

        # Emergency load varies by time - higher during evening/night
        if 16 <= current_hour <= 23:  # Peak hours
            base_multiplier = 1.3
        elif 0 <= current_hour <= 6:  # Late night
            base_multiplier = 0.7
        else:  # Regular hours
            base_multiplier = 1.0

        # Generate realistic load pattern
        load_data = []
        for i in range(7):
            # Simulate data for last 7 time periods
            base_load = 40 + (i * 5)  # Slight increase over time
            adjusted_load = int(base_load * base_multiplier)
            variation = random.randint(-8, 12)
            final_load = max(15, min(85, adjusted_load + variation))
            load_data.append(final_load)

        return load_data

    def _get_current_alerts(self) -> List[Dict[str, Any]]:
        """Get current system alerts"""
        alerts = []

        # ICU capacity alert
        icu_occupancy = self.base_metrics["icuOccupancy"]
        if icu_occupancy > 85:
            alerts.append(
                {
                    "type": "warning",
                    "message": f"ICU occupancy high: {icu_occupancy}%",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high",
                }
            )
        elif icu_occupancy > 90:
            alerts.append(
                {
                    "type": "critical",
                    "message": f"ICU occupancy critical: {icu_occupancy}%",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "critical",
                }
            )

        # Staff shortage alerts
        staff = self._get_staff_availability()
        if staff["doctors"] < 50:
            alerts.append(
                {
                    "type": "warning",
                    "message": f'Doctor availability low: {staff["doctors"]}%',
                    "timestamp": datetime.now().isoformat(),
                    "priority": "medium",
                }
            )

        if staff["nurses"] < 40:
            alerts.append(
                {
                    "type": "warning",
                    "message": f'Nurse availability low: {staff["nurses"]}%',
                    "timestamp": datetime.now().isoformat(),
                    "priority": "medium",
                }
            )

        # Random maintenance alerts (simulate real environment)
        if random.random() < 0.1:  # 10% chance
            alerts.append(
                {
                    "type": "info",
                    "message": "Scheduled maintenance: MRI Unit 2",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "low",
                }
            )

        return alerts

    def _get_quick_stats(self) -> Dict[str, Any]:
        """Get additional quick statistics"""
        current_time = datetime.now()

        return {
            "totalPatients": random.randint(180, 220),
            "admissions": {
                "today": random.randint(8, 25),
                "week": random.randint(85, 140),
            },
            "discharges": {
                "today": random.randint(5, 20),
                "week": random.randint(80, 130),
            },
            "operatingRooms": {"active": random.randint(3, 8), "total": 12},
            "emergencyWaitTime": f"{random.randint(15, 45)} minutes",
            "bedAvailability": {
                "icu": max(0, 24 - int(24 * (self.base_metrics["icuOccupancy"] / 100))),
                "general": random.randint(15, 45),
                "emergency": random.randint(2, 8),
            },
            "criticalEquipment": {
                "ventilators": {"available": random.randint(8, 15), "total": 20},
                "defibrillators": {"available": random.randint(12, 18), "total": 20},
            },
        }

    def get_section_data(self, section: str) -> Dict[str, Any]:
        """
        Get data specific to a dashboard section

        Args:
            section: Section name ('dashboard', 'forecasting', 'alerts', 'resources')

        Returns:
            Section-specific data
        """
        if section == "dashboard":
            return self.get_dashboard_data()

        elif section == "forecasting":
            return self._get_forecasting_data()

        elif section == "alerts":
            return self._get_alerts_data()

        elif section == "resources":
            return self._get_resources_data()

        else:
            return self.get_dashboard_data()

    def _get_forecasting_data(self) -> Dict[str, Any]:
        """Get forecasting-specific data"""
        future_hours = []
        current_time = datetime.now()

        # Generate 24-hour forecast
        for i in range(24):
            future_time = current_time + timedelta(hours=i)
            predicted_occupancy = self._predict_occupancy(future_time)
            future_hours.append(
                {
                    "hour": future_time.strftime("%H:00"),
                    "icuOccupancy": predicted_occupancy,
                    "expectedAdmissions": random.randint(1, 5),
                    "expectedDischarges": random.randint(0, 4),
                }
            )

        return {
            "forecast": future_hours,
            "trends": {
                "occupancyTrend": "increasing" if random.random() > 0.5 else "stable",
                "admissionTrend": "normal",
                "resourceTrend": "adequate",
            },
            "recommendations": [
                "Monitor ICU capacity closely during evening hours",
                "Consider scheduling elective procedures for morning slots",
                "Ensure adequate nursing staff for night shift",
            ],
        }

    def _get_alerts_data(self) -> Dict[str, Any]:
        """Get alerts-specific data"""
        return {
            "active": self._get_current_alerts(),
            "recent": self._get_recent_alerts(),
            "statistics": {
                "totalToday": random.randint(3, 12),
                "resolvedToday": random.randint(2, 8),
                "averageResponseTime": f"{random.randint(5, 15)} minutes",
            },
        }

    def _get_resources_data(self) -> Dict[str, Any]:
        """Get resources-specific data"""
        return {
            "equipment": self._get_equipment_status(),
            "medications": self._get_medication_inventory(),
            "facilities": self._get_facility_status(),
            "budget": {
                "monthlyBudget": 2500000,
                "spent": random.randint(1800000, 2200000),
                "emergencyFund": 500000,
            },
        }

    def _predict_occupancy(self, target_time: datetime) -> int:
        """Predict ICU occupancy for a given time"""
        hour = target_time.hour
        base_occupancy = self.base_metrics["icuOccupancy"]

        # Time-based patterns
        if 20 <= hour <= 23 or 0 <= hour <= 6:  # Night hours - typically higher
            modifier = random.randint(5, 15)
        elif 8 <= hour <= 12:  # Morning - discharges and rounds
            modifier = random.randint(-10, 5)
        else:  # Afternoon/evening
            modifier = random.randint(-5, 10)

        return max(40, min(95, base_occupancy + modifier))

    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts (last 24 hours)"""
        alerts = []
        for i in range(random.randint(5, 15)):
            alert_time = datetime.now() - timedelta(hours=random.randint(1, 24))
            alerts.append(
                {
                    "type": random.choice(["info", "warning", "critical"]),
                    "message": random.choice(
                        [
                            "Equipment maintenance completed",
                            "Patient transfer completed",
                            "Medication inventory updated",
                            "Staff shift change completed",
                            "Emergency response activated",
                        ]
                    ),
                    "timestamp": alert_time.isoformat(),
                    "resolved": random.choice([True, False]),
                }
            )

        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)

    def _get_equipment_status(self) -> Dict[str, Any]:
        """Get equipment status information"""
        return {
            "ventilators": {
                "total": 20,
                "available": random.randint(8, 15),
                "maintenance": 2,
            },
            "defibrillators": {
                "total": 20,
                "available": random.randint(15, 18),
                "maintenance": 1,
            },
            "xrayMachines": {
                "total": 6,
                "available": random.randint(4, 6),
                "maintenance": 0,
            },
            "ctScanners": {
                "total": 3,
                "available": random.randint(2, 3),
                "maintenance": 0,
            },
            "mriMachines": {
                "total": 2,
                "available": random.randint(1, 2),
                "maintenance": 0,
            },
        }

    def _get_medication_inventory(self) -> Dict[str, Any]:
        """Get medication inventory status"""
        return {
            "critical": {
                "morphine": {
                    "current": random.randint(80, 120),
                    "minimum": 50,
                    "status": "adequate",
                },
                "epinephrine": {
                    "current": random.randint(25, 40),
                    "minimum": 20,
                    "status": "adequate",
                },
                "insulin": {
                    "current": random.randint(150, 200),
                    "minimum": 100,
                    "status": "good",
                },
            },
            "lowStock": random.choice(
                [[], ["Antibiotics Type A"], ["Pain medication"], []]
            ),
            "expiringSoon": random.choice(
                [[], ["Emergency medications"], ["Vitamins"], []]
            ),
        }

    def _get_facility_status(self) -> Dict[str, Any]:
        """Get facility status information"""
        return {
            "powerSystems": {
                "main": "operational",
                "backup": "ready",
                "lastTest": "2024-12-10",
            },
            "hvacSystems": {
                "heating": "operational",
                "cooling": "operational",
                "ventilation": "operational",
            },
            "elevators": {
                "total": 8,
                "operational": random.randint(7, 8),
                "maintenance": 0,
            },
            "emergencySystems": {
                "fireAlarm": "operational",
                "sprinklers": "operational",
                "emergencyLighting": "operational",
            },
            "waterSystems": {
                "main": "operational",
                "hot": "operational",
                "backup": "ready",
            },
        }


# Global instance
dashboard_service = DashboardService()
