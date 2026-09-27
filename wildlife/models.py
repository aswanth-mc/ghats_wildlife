from django.db import models
from django.contrib.gis.db import models

# Create your models here.



class WildlifeSighting(models.Model):
  """Stores real-world animal observation points (from iNaturalist or citizen reports)."""

  SPECIES_CHOICES = [
      ("Elephas maximus", "Asian Elephant"),
      ("Panthera tigris", "Bengal Tiger"),
      ("Panthera pardus", "Indian Leopard"),
      ("Bos gaurus", "Gaur"),
  ]

  species = models.CharField(max_length=100, choices=SPECIES_CHOICES)
  common_name = models.CharField(max_length=100, blank=True)
  observed_at = models.DateTimeField(null=True, blank=True)

  # Geometry field storing (longitude, latitude) in WGS 84 (SRID 4326)
  location = models.PointField(srid=4326)

  source = models.CharField(max_length=50, default="iNaturalist")
  external_id = models.CharField(
      max_length=100, unique=True, null=True, blank=True
  )
  quality_grade = models.CharField(max_length=50, default="research")
  image_url = models.URLField(max_length=500, blank=True, null=True)

  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-observed_at"]
    indexes = [
        models.Index(fields=["species"]),
        models.Index(fields=["observed_at"]),
    ]

  def __str__(self):
    return (
        f"{self.common_name or self.species} at ({self.location.y:.3f},"
        f" {self.location.x:.3f})"
    )


class ConflictHotspot(models.Model):
  """Stores spatial cluster boundaries computed by analytics jobs (Sprint 3)."""

  RISK_LEVELS = [
      ("low", "Low Risk"),
      ("moderate", "Moderate Risk"),
      ("high", "High Risk"),
  ]

  cluster_id = models.IntegerField()
  # Stores the convex hull polygon enclosing the cluster points
  perimeter = models.PolygonField(srid=4326)
  incident_count = models.PositiveIntegerField()
  risk_level = models.CharField(
      max_length=20, choices=RISK_LEVELS, default="low"
  )
  last_computed = models.DateTimeField(auto_now=True)

  def __str__(self):
    return f"Hotspot #{self.cluster_id} [{self.risk_level.upper()}] - {self.incident_count} events"