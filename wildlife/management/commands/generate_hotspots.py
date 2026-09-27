from django.core.management.base import BaseCommand
from wildlife.services.hotspot_engine import compute_hotspots
from wildlife.models import ConflictHotspot

class Command(BaseCommand):
    help = "Run DBSCAN clustering to generate wildlife conflict hotspots."

    def add_arguments(self, parser):
        parser.add_argument('--eps', type=float, default=10.0, help="DBSCAN epsilon radius in kilometers.")
        parser.add_argument('--min-samples', type=int, default=3, help="Minimum sightings per cluster.")

    def handle(self, *args, **options):
        eps_km = options['eps']
        min_samples = options['min_samples']

        self.stdout.write(self.style.NOTICE(f"Computing hotspots with eps={eps_km}km, min_samples={min_samples}..."))
        
        count = compute_hotspots(eps_km=eps_km, min_samples=min_samples)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {count} conflict hotspot zones!"))

        # Print quick summary
        for spot in ConflictHotspot.objects.all():
            self.stdout.write(f"- Cluster #{spot.cluster_id}: {spot.incident_count} incidents [{spot.risk_level.upper()}]")