#!/usr/bin/env python3
"""
Test script for the dashboard service
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_dashboard_service():
    """Test the dashboard service functionality"""
    try:
        from src.services.dashboard_service import dashboard_service

        print("🧪 Testing Dashboard Service")
        print("=" * 50)

        # Test basic dashboard data
        print("\n📊 Testing basic dashboard data...")
        data = dashboard_service.get_dashboard_data()
        print(f"✅ ICU Occupancy: {data['icuOccupancy']}%")
        print(
            f"✅ Staff Availability: Doctors {data['staffAvailability']['doctors']}%, Nurses {data['staffAvailability']['nurses']}%"
        )
        print(f"✅ Tool Usage: {data['toolUsage']}")
        print(f"✅ Emergency Load: {data['emergencyLoad']}")
        print(f"✅ Alerts: {len(data['alerts'])} active alerts")

        # Test section-specific data
        print("\n📈 Testing section-specific data...")
        sections = ["dashboard", "forecasting", "alerts", "resources"]

        for section in sections:
            section_data = dashboard_service.get_section_data(section)
            print(f"✅ {section.capitalize()}: {len(section_data)} data points")

        # Test forecasting data
        print("\n🔮 Testing forecasting data...")
        forecast_data = dashboard_service.get_section_data("forecasting")
        print(f"✅ Forecast hours: {len(forecast_data['forecast'])}")
        print(f"✅ Trends: {forecast_data['trends']}")
        print(f"✅ Recommendations: {len(forecast_data['recommendations'])}")

        # Test alerts data
        print("\n🚨 Testing alerts data...")
        alerts_data = dashboard_service.get_section_data("alerts")
        print(f"✅ Active alerts: {len(alerts_data['active'])}")
        print(f"✅ Recent alerts: {len(alerts_data['recent'])}")
        print(f"✅ Statistics: {alerts_data['statistics']}")

        # Test resources data
        print("\n🏥 Testing resources data...")
        resources_data = dashboard_service.get_section_data("resources")
        print(f"✅ Equipment types: {len(resources_data['equipment'])}")
        print(
            f"✅ Critical medications: {len(resources_data['medications']['critical'])}"
        )
        print(f"✅ Facility systems: {len(resources_data['facilities'])}")

        print("\n" + "=" * 50)
        print("🎉 All tests passed! Dashboard service is working correctly.")

        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_json_serialization():
    """Test that all data can be JSON serialized"""
    try:
        from src.services.dashboard_service import dashboard_service

        print("\n🔧 Testing JSON serialization...")

        sections = ["dashboard", "forecasting", "alerts", "resources"]
        for section in sections:
            data = dashboard_service.get_section_data(section)
            json_str = json.dumps(data, indent=2)
            print(f"✅ {section.capitalize()}: {len(json_str)} characters")

        print("✅ All data is JSON serializable")
        return True

    except Exception as e:
        print(f"❌ JSON serialization test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("🏥 Hospital Dashboard Service Test")
    print("=" * 60)

    success = True
    success &= test_dashboard_service()
    success &= test_json_serialization()

    if success:
        print("\n🎉 All tests completed successfully!")
        print("The dashboard service is ready for use.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
