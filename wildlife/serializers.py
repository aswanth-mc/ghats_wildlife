from rest_framework_gis.serializers import GeoFeatureModelSerializer
from wildlife.models import ConflictHotspot, WildlifeSighting


class ConflictHotspotGeoSerializer(GeoFeatureModelSerializer):

  class Meta:
    model = ConflictHotspot
    geo_field = "perimeter"
    fields = ("id", "cluster_id", "incident_count", "risk_level", "last_computed")


class WildlifeSightingGeoSerializer(GeoFeatureModelSerializer):

  class Meta:
    model = WildlifeSighting
    geo_field = "location"
    fields = (
        "id",
        "species",
        "common_name",
        "observed_at",
        "source",
        "image_url",
    )