# Western Ghats Wildlife Movement & Hotspot Alert System

An end-to-end spatial data analytics and GIS monitoring platform designed to identify wildlife corridors and human-wildlife conflict zones across the Western Ghats ecosystem. 

The system ingests open biodiversity data, clusters high-density activity corridors using unsupervised machine learning (**DBSCAN**), and serves interactive risk polygons over an interactive web map.

---

## Key Features

- **Automated Open Data Ingestion (ETL):** Custom Django management commands pull verified, research-grade observation records directly from the public **iNaturalist API** using a bounding box covering the Western Ghats.
- **Spatial Relational Database:** Powered by **PostgreSQL** and **PostGIS**, storing high-precision geometry types (`PointField` and `PolygonField`) with spatial indexing (GiST).
- **Unsupervised Spatial Analytics:** Employs **DBSCAN** clustering with a spherical **Haversine metric** via `scikit-learn` to cluster movement trails into convex hull risk perimeters while filtering out isolated noise.
- **Native GeoJSON API:** Django endpoints stream standards-compliant GeoJSON collections for lightweight front-end mapping.
- **Interactive Leaflet Dashboard:** Dark-themed operational dashboard rendering topographic terrain maps, dynamic risk layers (High, Moderate, Low), and individual sighting markers with metadata and field photos.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend & Web Framework** | Python 3, Django, GeoDjango, Django REST Framework |
| **Spatial Database** | PostgreSQL, PostGIS |
| **Data Analytics & ML** | NumPy, scikit-learn (DBSCAN), GeoPandas, Shapely |
| **Frontend & GIS Visualization** | Leaflet.js, OpenTopoMap, Vanilla CSS3 / HTML5 |
| **External APIs** | iNaturalist v1 REST API |

---

## System Architecture

```text
[ iNaturalist API ]
        │
        ▼ (sync_inaturalist CLI)
[ GeoDjango ORM ] ──► [ PostgreSQL / PostGIS ]
                            │
                            ▼
           [ DBSCAN Clustering Engine (generate_hotspots) ]
                            │
                            ▼ (Convex Hulls & Risk Scoring)
                 [ ConflictHotspot Table ]
                            │
                            ▼ (GeoJSON Endpoints)
             [ Leaflet.js Web Dashboard ]
