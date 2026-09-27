from datetime import datetime
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
import requests
from wildlife.models import WildlifeSighting


class Command(BaseCommand):
  help = "Fetch recent wildlife observation records from iNaturalist across the Western Ghats."

  def add_arguments(self, parser):
    parser.add_argument(
        "--pages",
        type=int,
        default=2,
        help="Number of result pages to fetch (100 records per page).",
    )

  def handle(self, *args, **options):
    # Western Ghats Bounding Box
    # SW: 8.0 N, 74.5 E | NE: 15.0 N, 77.8 E
    bbox = {"swlat": 8.0, "swlng": 74.5, "nelat": 15.0, "nelng": 77.8}

    # Species Taxon IDs on iNaturalist:
    # Asian Elephant: 43694, Bengal Tiger: 41954, Leopard: 41967, Gaur: 48332
    target_taxa = [
        (43694, "Elephas maximus", "Asian Elephant"),
        (41954, "Panthera tigris", "Bengal Tiger"),
        (41967, "Panthera pardus", "Indian Leopard"),
        (48332, "Bos gaurus", "Gaur"),
    ]

    base_url = "https://api.inaturalist.org/v1/observations"
    pages_to_fetch = options["pages"]

    total_created = 0
    total_skipped = 0

    self.stdout.write(
        self.style.NOTICE("Connecting to iNaturalist API for Western Ghats...")
    )

    for taxon_id, sci_name, common_name in target_taxa:
      self.stdout.write(f"Fetching records for: {common_name} ({sci_name})...")

      for page in range(1, pages_to_fetch + 1):
        params = {
            "taxon_id": taxon_id,
            "nelat": bbox["nelat"],
            "nelng": bbox["nelng"],
            "swlat": bbox["swlat"],
            "swlng": bbox["swlng"],
            "quality_grade": "research",  # High data fidelity
            "per_page": 100,
            "page": page,
            "order": "desc",
            "order_by": "observed_on",
        }

        try:
          response = requests.get(base_url, params=params, timeout=15)
          response.raise_for_status()
          data = response.json()
        except requests.RequestException as exc:
          self.stderr.write(f"Failed to fetch page {page}: {exc}")
          break

        results = data.get("results", [])
        if not results:
          break

        for item in results:
          ext_id = f"inat_{item['id']}"

          # Check if already ingested to avoid duplicates
          if WildlifeSighting.objects.filter(external_id=ext_id).exists():
            total_skipped += 1
            continue

          geojson = item.get("geojson")
          if not geojson or "coordinates" not in geojson:
            continue

          # NOTE: GeoJSON standard order is [longitude, latitude]
          lon, lat = geojson["coordinates"]

          # Parse observed timestamp if available
          observed_str = item.get("time_observed_at") or item.get(
              "observed_on"
          )
          observed_at = None
          if observed_str:
            try:
              # Handle ISO format strings
              observed_at = datetime.fromisoformat(
                  observed_str.replace("Z", "+00:00")
              )
            except ValueError:
              pass

          # Get representative photo if present
          photo_url = None
          photos = item.get("photos", [])
          if photos:
            photo_url = photos[0].get("url")

          # PostGIS Point takes (x, y) which corresponds to (lon, lat)
          point = Point(x=float(lon), y=float(lat), srid=4326)

          WildlifeSighting.objects.create(
              species=sci_name,
              common_name=common_name,
              observed_at=observed_at,
              location=point,
              source="iNaturalist",
              external_id=ext_id,
              quality_grade=item.get("quality_grade", "research"),
              image_url=photo_url,
          )
          total_created += 1

    self.stdout.write(
        self.style.SUCCESS(
            f"Sync complete! Created: {total_created} new records, Skipped:"
            f" {total_skipped} existing records."
        )
    )