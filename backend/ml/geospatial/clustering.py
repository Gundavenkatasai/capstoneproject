"""
CivicMind AI — Spatial Clustering Engine (DBSCAN + Haversine)
Phase 6 Geospatial Grievance Intelligence.

Performs density-based spatial clustering on municipal grievance coordinates
using spherical Haversine metric. Computes cluster centroids, dynamic radiation
radii, complaint counts, and strict operational vs synthetic separation.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
import numpy as np
from sklearn.cluster import DBSCAN


EARTH_RADIUS_KM = 6371.0088
EARTH_RADIUS_METERS = 6371008.8


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two points on Earth in meters.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c


class SpatialClusterer:
    """
    Density-Based Spatial Clustering of Applications with Noise (DBSCAN)
    calibrated for municipal grievance coordinates using Haversine distance metric.
    """

    def __init__(
        self,
        radius_km: float = 0.5,
        min_samples: int = 2,
    ):
        """
        :param radius_km: Maximum epsilon neighborhood radius in kilometers (default: 500m = 0.5km).
        :param min_samples: Minimum complaints to form a high-density civic cluster (default: 2).
        """
        self.radius_km = radius_km
        self.eps_radians = radius_km / EARTH_RADIUS_KM
        self.min_samples = min_samples

    def cluster_grievances(
        self,
        grievances: List[Dict[str, Any]],
        filter_synthetic: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Clusters a collection of grievance records into geographic hotspots.

        SCIENTIFIC SEPARATION:
        If `filter_synthetic=True`, records originating from synthetic benchmarks
        (e.g., id prefixed with 'SYN-', or metadata with is_synthetic=True) are
        strictly excluded from operational cluster generation.
        """
        if not grievances:
            return []

        # Segregate operational vs synthetic benchmark data
        eligible: List[Dict[str, Any]] = []
        for g in grievances:
            is_synth = (
                g.get("is_synthetic") is True
                or str(g.get("id", "")).startswith("SYN-")
                or g.get("source") == "synthetic_benchmark"
                or (isinstance(g.get("metadata"), dict) and g.get("metadata", {}).get("is_synthetic") is True)
            )
            if filter_synthetic and is_synth:
                continue

            lat = g.get("latitude") or g.get("lat")
            lng = g.get("longitude") or g.get("lng")
            if lat is not None and lng is not None:
                try:
                    lat_f = float(lat)
                    lng_f = float(lng)
                    if -90.0 <= lat_f <= 90.0 and -180.0 <= lng_f <= 180.0:
                        eligible.append({**g, "_lat": lat_f, "_lng": lng_f})
                except (ValueError, TypeError):
                    continue

        if len(eligible) < self.min_samples:
            return []

        # Convert coordinates to radians: shape (N, 2) [latitude, longitude]
        coords_deg = np.array([[item["_lat"], item["_lng"]] for item in eligible])
        coords_rad = np.radians(coords_deg)

        # Execute DBSCAN with haversine metric
        db = DBSCAN(
            eps=self.eps_radians,
            min_samples=self.min_samples,
            metric="haversine",
            algorithm="ball_tree",
        )
        labels = db.fit_predict(coords_rad)

        clusters: List[Dict[str, Any]] = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                # Noise points that did not reach cluster density
                continue

            cluster_members = [eligible[i] for i, l in enumerate(labels) if l == label]
            if len(cluster_members) < self.min_samples:
                continue

            # Compute centroid
            member_lats = [m["_lat"] for m in cluster_members]
            member_lngs = [m["_lng"] for m in cluster_members]
            centroid_lat = float(np.mean(member_lats))
            centroid_lng = float(np.mean(member_lngs))

            # Compute radiation radius (max distance to any member in meters, minimum 120m)
            max_dist = max(
                haversine_distance_meters(centroid_lat, centroid_lng, m["_lat"], m["_lng"])
                for m in cluster_members
            )
            radius_meters = max(120, int(math.ceil(max_dist)))

            # Extract member IDs and characteristics
            related_ids = [str(m.get("id")) for m in cluster_members if m.get("id")]

            # Compute category mode
            categories = [m.get("category", "General Civic") for m in cluster_members if m.get("category")]
            dominant_category = max(set(categories), key=categories.count) if categories else "General Civic"

            # Compute ward mode
            wards = [m.get("ward", "Central Ward") for m in cluster_members if m.get("ward")]
            dominant_ward = max(set(wards), key=wards.count) if wards else "Central Ward"

            # Compute zone mode
            zones = [m.get("zone", "Central Zone") for m in cluster_members if m.get("zone")]
            dominant_zone = max(set(zones), key=zones.count) if zones else "Central Zone"

            # Compute cluster severity score (0 to 100)
            priority_weights = {"critical": 30, "high": 20, "medium": 10, "low": 5}
            priority_score = sum(
                priority_weights.get(str(m.get("priority", "medium")).lower(), 10)
                for m in cluster_members
            )
            count_factor = min(35, len(cluster_members) * 7)
            raw_severity = 20 + priority_score // len(cluster_members) + count_factor
            severity_score = min(100, max(15, raw_severity))

            clusters.append({
                "cluster_label": int(label),
                "latitude": round(centroid_lat, 6),
                "longitude": round(centroid_lng, 6),
                "radius_meters": radius_meters,
                "complaint_count": len(cluster_members),
                "related_complaint_ids": related_ids,
                "category": dominant_category,
                "ward": dominant_ward,
                "zone": dominant_zone,
                "severity_score": severity_score,
                "members": cluster_members,
                "is_synthetic": any(
                    m.get("is_synthetic") is True or str(m.get("id", "")).startswith("SYN-")
                    for m in cluster_members
                ),
            })

        # Sort clusters by severity descending
        clusters.sort(key=lambda c: (c["severity_score"], c["complaint_count"]), reverse=True)
        return clusters
