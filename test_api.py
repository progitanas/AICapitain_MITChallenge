#!/usr/bin/env python
"""Test script for AI Captain API"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("🔍 TEST 1: Health Check")
    r = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.json()}")
    return r.status_code == 200

def test_waypoints():
    print("\n🌍 TEST 2: Waypoints List")
    r = requests.get(f"{BASE_URL}/api/v1/waypoints")
    if r.status_code != 200:
        print(f"  ❌ Error: {r.status_code}")
        return False
    
    data = r.json()
    print(f"  ✅ Status: 200 OK")
    print(f"  Total Waypoints: {len(data['waypoints'])}")
    print("  Sample Waypoints:")
    for wp in data['waypoints'][:3]:
        print(f"    - {wp['id']}: {wp['name']}")
    return True

def test_route_optimization():
    print("\n📍 TEST 3: Route Optimization (Singapore → Hamburg)")
    
    payload = {
        "vessel": {
            "mmsi": "636016829",
            "imo": "9123456",
            "name": "Maritime Explorer",
            "call_sign": "CALL1",
            "dimensions": {
                "length_m": 190,
                "beam_m": 32,
                "draught_m": 11,
                "depth_m": 18
            },
            "type_code": 70,
            "latitude": 1.3521,
            "longitude": 103.8198,
            "sog_knots": 15,
            "cog_degrees": 90,
            "heading_degrees": 88,
            "nav_status": 0
        },
        "start_port_id": "SG",
        "end_port_id": "HA",
        "weight_time": 1.0,
        "weight_cost": 1.0,
        "weight_risk": 1.0,
        "fuel_price_per_ton": 500.0
    }
    
    r = requests.post(f"{BASE_URL}/api/v1/route/optimize", json=payload)
    if r.status_code != 200:
        print(f"  ❌ Error: {r.status_code}")
        print(f"  Message: {r.text}")
        return False
    
    route = r.json()
    print(f"  ✅ Status: 200 OK")
    print(f"  Route Waypoints: {len(route['route'])}")
    print(f"  Path: {' → '.join([w['id'] for w in route['route']])}")
    print(f"  Distance: {route['total_distance_nm']:.0f} NM")
    print(f"  Time: {route['total_time_hours']:.1f} hours ({route['total_time_hours']/24:.1f} days)")
    print(f"  Fuel: {route['total_fuel_tons']:.1f} tons")
    print(f"  Cost: ${route['total_cost_usd']:.0f}")
    print(f"  Risk: {route['total_risk_score']:.2f}")
    return True

def main():
    print("=" * 60)
    print("🚢 AI CAPTAIN API TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Waypoints", test_waypoints()))
    results.append(("Route Optimization", test_route_optimization()))
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + ("✅ ALL TESTS PASSED!" if all_passed else "❌ SOME TESTS FAILED"))
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
