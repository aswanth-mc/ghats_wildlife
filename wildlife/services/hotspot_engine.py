import numpy as np
from sklearn.cluster import DBSCAN
from django.contrib.gis.geos import Polygon, MultiPoint
from wildlife.models import WildlifeSighting, ConflictHotspot

def compute_hotspots(eps_km=10.0, min_samples=3):
    """
    Computes spatial density clusters from WildlifeSighting points using DBSCAN.
    Saves the computed polygon perimeters into ConflictHotspot.
    """
    sightings = list(WildlifeSighting.objects.all())
    
    if len(sightings) < min_samples:
        print("Not enough sightings to compute clusters.")
        return 0

    # Extract coordinates: [latitude, longitude]
    # Scikit-learn haversine metric requires radians: [lat_rad, lon_rad]
    coords = np.array([[s.location.y, s.location.x] for s in sightings])
    coords_rad = np.radians(coords)

    # Earth radius in kilometers
    EARTH_RADIUS_KM = 6371.0088
    eps_rad = eps_km / EARTH_RADIUS_KM

    # Run DBSCAN with Haversine distance metric
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric='haversine', algorithm='ball_tree')
    cluster_labels = db.fit_predict(coords_rad)

    # Clear previous calculated hotspots
    ConflictHotspot.objects.all().delete()

    unique_labels = set(cluster_labels)
    created_count = 0

    for label in unique_labels:
        # Label -1 is noise (isolated sightings that don't form a cluster)
        if label == -1:
            continue

        # Get sightings belonging to this cluster
        cluster_indices = np.where(cluster_labels == label)[0]
        cluster_sightings = [sightings[idx] for idx in cluster_indices]
        incident_count = len(cluster_sightings)

        # Collect points to create a bounding polygon
        points = [s.location for s in cluster_sightings]
        multi_pt = MultiPoint(points)

        # Build polygon perimeter
        if incident_count >= 3:
            # Convex hull wraps the cluster points
            hull = multi_pt.convex_hull
            
            # If the points are in a straight line, buffer slightly to create a valid 2D polygon
            if hull.geom_type != 'Polygon':
                hull = hull.buffer(0.02)  # ~2 km buffer
        else:
            hull = multi_pt.buffer(0.02)

        # Determine risk classification based on incident volume
        if incident_count >= 10:
            risk = 'high'
        elif incident_count >= 5:
            risk = 'moderate'
        else:
            risk = 'low'

        # Ensure geometry is a valid Polygon
        if hull.geom_type == 'Polygon':
            ConflictHotspot.objects.create(
                cluster_id=int(label),
                perimeter=hull,
                incident_count=incident_count,
                risk_level=risk
            )
            created_count += 1

    return created_count