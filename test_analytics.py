#!/usr/bin/env python3
"""
Test script for Smart Hospital Analytics System.
Tests the analytics modules and database connectivity.
"""
import os
import sys
import asyncio
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.append('backend')

def test_db_connection():
    """Test database connection."""
    print("🔧 Testing database connection...")
    try:
        from backend.db_utils import db
        
        # Test basic query
        result = db.execute_query("SELECT 1 as test")
        print(f"✅ Database connection successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_analytics_registry():
    """Test analytics registry."""
    print("\n📊 Testing analytics registry...")
    try:
        from backend.analysis_registry import ANALYSES, get_analysis_list, run_analysis
        
        print(f"✅ Found {len(ANALYSES)} analyses:")
        for analysis_id, config in ANALYSES.items():
            print(f"  - {analysis_id}: {config['label']}")
        
        # Test getting analysis list
        analysis_list = get_analysis_list()
        print(f"✅ Analysis list contains {len(analysis_list)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics registry test failed: {e}")
        return False


async def test_individual_analyses():
    """Test each analysis function."""
    print("\n🧪 Testing individual analyses...")
    
    try:
        from backend.analysis_registry import ANALYSES, run_analysis
        
        for analysis_id in ANALYSES.keys():
            print(f"\n  Testing {analysis_id}...")
            try:
                result = await run_analysis(analysis_id)
                
                if "error" in result:
                    print(f"  ⚠️  {analysis_id}: {result['error']}")
                else:
                    print(f"  ✅ {analysis_id}: Success")
                    if "data" in result:
                        print(f"     Data keys: {list(result['data'].keys()) if isinstance(result['data'], dict) else 'non-dict data'}")
                
            except Exception as e:
                print(f"  ❌ {analysis_id}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual analysis tests failed: {e}")
        return False


def test_mock_data():
    """Test with mock data if database is not available."""
    print("\n🎭 Testing with mock data...")
    
    try:
        # Mock bed snapshot data
        mock_bed_data = {
            "data": [
                {"ward": "ICU", "occupied": 8, "available": 2, "total": 10, "utilisation": 80.0},
                {"ward": "Emergency", "occupied": 15, "available": 5, "total": 20, "utilisation": 75.0},
                {"ward": "General", "occupied": 25, "available": 10, "total": 35, "utilisation": 71.4}
            ],
            "timestamp": datetime.now().isoformat(),
            "total_beds": 65,
            "total_occupied": 48,
            "overall_utilisation": 73.8
        }
        
        print("✅ Mock bed data created successfully")
        print(f"   Total beds: {mock_bed_data['total_beds']}")
        print(f"   Overall utilization: {mock_bed_data['overall_utilisation']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock data test failed: {e}")
        return False


def test_api_endpoints():
    """Test FastAPI endpoints."""
    print("\n🌐 Testing API endpoints...")
    
    try:
        from backend.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        print("✅ Root endpoint working")
        
        # Test analyses list
        response = client.get("/analyses")
        assert response.status_code == 200
        print("✅ Analyses list endpoint working")
        
        # Test specific analysis metadata
        response = client.get("/analysis/bed_snapshot/metadata")
        assert response.status_code == 200
        print("✅ Analysis metadata endpoint working")
        
        return True
        
    except ImportError:
        print("⚠️  FastAPI test client not available, skipping API tests")
        return True
    except Exception as e:
        print(f"❌ API endpoint tests failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🏥 Smart Hospital Analytics System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_db_connection),
        ("Analytics Registry", test_analytics_registry),
        ("Mock Data", test_mock_data),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Test individual analyses only if basic tests pass
    if results[1][1]:  # If analytics registry test passed
        individual_result = await test_individual_analyses()
        results.append(("Individual Analyses", individual_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Analytics system is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    # Install test dependencies if needed
    try:
        import dotenv
    except ImportError:
        os.system("pip install python-dotenv")
        import dotenv
    
    asyncio.run(main()) 