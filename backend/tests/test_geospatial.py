"""
CivicMind AI — Phase 6 Geospatial Intelligence & Simulator Test Suite
Verifies DBSCAN spatial clustering, synthetic data segregation, Haversine metrics,
Early-Warning Radar velocity surges, counterfactual simulator, and REST APIs.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient

from ml.geospatial.clustering import SpatialClusterer, haversine_distance_meters
from ml.geospatial.radar import EarlyWarningRadar
from app.services.simulator_service import simulator_service
from app.schemas.simulator import SimulatorInputSchema


# ==============================================================================
# Unit Tests: Haversine Metric & Spatial Clustering
# ==============================================================================

def test_haversine_distance_meters():
    # Distance between two known coordinates in Hyderabad (~1.1 km)
    # Charminar (17.3616, 78.4747) to Mecca Masjid (17.3605, 78.4735) ~170m
    dist = haversine_distance_meters(17.3616, 78.4747, 17.3605, 78.4735)
    assert 120.0 <= dist <= 220.0

    # Distance to identical point is 0
    assert haversine_distance_meters(17.385, 78.486, 17.385, 78.486) == 0.0


def test_spatial_clustering_dense_points():
    clusterer = SpatialClusterer(radius_km=0.5, min_samples=2)

    # 3 tightly clustered points within 150m of each other
    tight_cluster = [
        {"id": "GRV-001", "latitude": 28.5244, "longitude": 77.1558, "category": "Water Supply", "ward": "Ward 14", "priority": "critical"},
        {"id": "GRV-002", "latitude": 28.5248, "longitude": 77.1560, "category": "Water Supply", "ward": "Ward 14", "priority": "high"},
        {"id": "GRV-003", "latitude": 28.5241, "longitude": 77.1555, "category": "Water Supply", "ward": "Ward 14", "priority": "high"},
        # 1 isolated noise point > 5km away
        {"id": "GRV-004", "latitude": 28.5999, "longitude": 77.2200, "category": "Electricity", "ward": "Ward 99", "priority": "low"},
    ]

    clusters = clusterer.cluster_grievances(tight_cluster, filter_synthetic=True)
    assert len(clusters) == 1
    c = clusters[0]
    assert c["complaint_count"] == 3
    assert "GRV-001" in c["related_complaint_ids"]
    assert "GRV-002" in c["related_complaint_ids"]
    assert "GRV-003" in c["related_complaint_ids"]
    assert "GRV-004" not in c["related_complaint_ids"]
    assert c["category"] == "Water Supply"
    assert c["ward"] == "Ward 14"
    assert c["radius_meters"] >= 120


def test_synthetic_data_segregation_invariant():
    """
    CRITICAL SCIENTIFIC INVARIANT:
    Synthetic benchmark records must NEVER be clustered into operational hotspots.
    """
    clusterer = SpatialClusterer(radius_km=0.5, min_samples=2)

    # Mixture of operational records and synthetic benchmark records
    mixed_data = [
        # Operational records
        {"id": "GRV-OP-1", "latitude": 28.5244, "longitude": 77.1558, "category": "Water Supply", "ward": "Ward 14", "is_synthetic": False},
        {"id": "GRV-OP-2", "latitude": 28.5248, "longitude": 77.1560, "category": "Water Supply", "ward": "Ward 14", "is_synthetic": False},
        # Synthetic benchmark records
        {"id": "SYN-BENCH-1", "latitude": 28.5245, "longitude": 77.1559, "category": "Water Supply", "ward": "Ward 14", "is_synthetic": True},
        {"id": "SYN-BENCH-2", "latitude": 28.5246, "longitude": 77.1561, "category": "Water Supply", "ward": "Ward 14", "source": "synthetic_benchmark"},
    ]

    # With filter_synthetic=True, synthetic records are filtered out
    clusters = clusterer.cluster_grievances(mixed_data, filter_synthetic=True)
    assert len(clusters) == 1
    c = clusters[0]
    assert c["complaint_count"] == 2
    assert "GRV-OP-1" in c["related_complaint_ids"]
    assert "GRV-OP-2" in c["related_complaint_ids"]
    assert "SYN-BENCH-1" not in c["related_complaint_ids"]
    assert "SYN-BENCH-2" not in c["related_complaint_ids"]


# ==============================================================================
# Unit Tests: Early-Warning Radar & Surge Metrics
# ==============================================================================

def test_early_warning_radar_velocity_and_trend():
    radar = EarlyWarningRadar()

    # Case 1: Increasing surge (+100% surge)
    surge_pct, trend = radar._calculate_surge_and_trend([2, 3, 4, 5, 6, 12])
    assert trend == "increasing"
    assert surge_pct > 20.0

    # Case 2: Decreasing trajectory
    surge_pct, trend = radar._calculate_surge_and_trend([12, 10, 8, 8, 7, 2])
    assert trend == "decreasing"
    assert surge_pct < -20.0

    # Case 3: Stable trajectory
    surge_pct, trend = radar._calculate_surge_and_trend([5, 5, 5, 5, 5, 5])
    assert trend == "stable"
    assert abs(surge_pct) < 20.0


def test_early_warning_radar_hotspot_generation():
    radar = EarlyWarningRadar()

    raw_cluster = {
        "cluster_label": 0,
        "latitude": 28.5244,
        "longitude": 77.1558,
        "radius_meters": 450,
        "complaint_count": 8,
        "related_complaint_ids": ["GRV-1", "GRV-2", "GRV-3"],
        "category": "Water Supply & Drainage",
        "ward": "Ward 14",
        "zone": "South Zone",
        "severity_score": 70,
        "is_synthetic": False,
    }

    hotspot = radar.process_cluster_to_hotspot(raw_cluster, hotspot_id="hotspot_test_1")

    assert hotspot["id"] == "hotspot_test_1"
    assert "Water" in hotspot["category"]
    assert hotspot["ward"] == "Ward 14"
    assert hotspot["risk_level"] in ("critical", "high")
    assert hotspot["risk_score"] >= 50
    assert hotspot["trend"] in ("increasing", "stable", "decreasing")
    assert len(hotspot["historical_velocity"]) == 6
    assert "hydraulic" in hotspot["recommended_action"].lower() or "pipeline" in hotspot["recommended_action"].lower()
    assert hotspot["source"] == "operational"


# ==============================================================================
# Unit Tests: Counterfactual Workload Simulator
# ==============================================================================

def test_simulator_baseline_metrics():
    baseline = simulator_service.get_baseline()
    assert baseline.currentBacklog == 1127
    assert baseline.simulatedBacklog == 1127
    assert baseline.currentAvgResolutionDays == 4.3
    assert baseline.simulatedAvgResolutionDays == 4.3
    assert baseline.currentSlaBreachRate == 12.8
    assert baseline.simulatedSlaBreachRate == 12.8
    assert len(baseline.departmentWorkload) == 6


def test_simulator_policy_intervention():
    # Inject 15 officers and 1.25x capacity enhancement
    input_scenario = SimulatorInputSchema(
        additionalOfficers=15,
        departmentCapacityMultiplier=1.25,
        workloadRedistributionPct=20,
        routingWeightAIFactor=0.85,
        escalationThresholdHours=36,
    )
    result = simulator_service.run_simulation(input_scenario)

    # Backlog must decrease significantly
    assert result.simulatedBacklog < result.currentBacklog
    assert result.simulatedBacklog >= 280

    # Resolution speed must improve (fewer days)
    assert result.simulatedAvgResolutionDays < result.currentAvgResolutionDays
    assert result.simulatedAvgResolutionDays >= 1.8

    # SLA breach rate must improve (lower breach %)
    assert result.simulatedSlaBreachRate < result.currentSlaBreachRate
    assert result.simulatedSlaBreachRate >= 3.2

    # Executive summary mentions officers and backlog
    assert "15 officers" in result.summary
    assert "reduction in system-wide active backlog" in result.summary


# ==============================================================================
# Integration Tests: FastAPI Endpoints (HTTP Client)
# ==============================================================================

@pytest.mark.asyncio
async def test_api_early_warning_hotspots(client: AsyncClient):
    response = await client.get("/api/v1/early-warning/hotspots")
    assert response.status_code == 200
    hotspots = response.json()
    assert isinstance(hotspots, list)
    assert len(hotspots) >= 1

    first = hotspots[0]
    assert "id" in first
    assert "title" in first
    assert "lat" in first
    assert "lng" in first
    assert "riskLevel" in first
    assert "riskScore" in first
    assert "trend" in first
    assert "recommendedAction" in first


@pytest.mark.asyncio
async def test_api_early_warning_filter_by_risk(client: AsyncClient):
    response = await client.get("/api/v1/early-warning/hotspots?riskLevel=critical")
    assert response.status_code == 200
    hotspots = response.json()
    for h in hotspots:
        assert h["riskLevel"] == "critical"


@pytest.mark.asyncio
async def test_api_early_warning_get_by_id(client: AsyncClient):
    # Fetch list first
    list_res = await client.get("/api/v1/early-warning/hotspots")
    assert list_res.status_code == 200
    first_id = list_res.json()[0]["id"]

    res = await client.get(f"/api/v1/early-warning/hotspots/{first_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == first_id


@pytest.mark.asyncio
async def test_api_early_warning_acknowledge(client: AsyncClient):
    # Fetch list first
    list_res = await client.get("/api/v1/early-warning/hotspots")
    assert list_res.status_code == 200
    first_id = list_res.json()[0]["id"]

    ack_res = await client.post(
        f"/api/v1/early-warning/hotspots/{first_id}/acknowledge",
        json={"notes": "Rapid task force team dispatched to sector 4"},
    )
    assert ack_res.status_code == 200
    updated = ack_res.json()
    assert updated["isAcknowledged"] is True
    assert "Acknowledged" in updated["recommendedAction"]


@pytest.mark.asyncio
async def test_api_early_warning_summary(client: AsyncClient):
    res = await client.get("/api/v1/early-warning/summary")
    assert res.status_code == 200
    data = res.json()
    assert "totalActiveHotspots" in data
    assert "criticalHotspots" in data
    assert "highRiskHotspots" in data
    assert "emergingSurges" in data
    assert "mostAffectedCategory" in data
    assert data["isOperational"] is True


@pytest.mark.asyncio
async def test_api_simulator_run(client: AsyncClient):
    payload = {
        "additionalOfficers": 20,
        "departmentCapacityMultiplier": 1.3,
        "workloadRedistributionPct": 15,
        "routingWeightAIFactor": 0.8,
        "escalationThresholdHours": 24,
    }
    res = await client.post("/api/v1/simulator/run", json=payload)
    assert res.status_code == 200
    result = res.json()

    assert result["currentBacklog"] == 1127
    assert result["simulatedBacklog"] < 1127
    assert result["simulatedAvgResolutionDays"] < 4.3
    assert result["simulatedSlaBreachRate"] < 12.8
    assert len(result["departmentWorkload"]) == 6
    assert "summary" in result


@pytest.mark.asyncio
async def test_api_simulator_baseline(client: AsyncClient):
    res = await client.get("/api/v1/simulator/baseline")
    assert res.status_code == 200
    result = res.json()
    assert result["currentBacklog"] == 1127
    assert result["simulatedBacklog"] == 1127
