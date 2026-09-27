from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from wildlife.models import ConflictHotspot, WildlifeSighting


# API: Returns calculated polygon zones as valid GeoJSON
def hotspots_geojson(request):
  data = serialize(
      'geojson',
      ConflictHotspot.objects.all(),
      geometry_field='perimeter',
      fields=('cluster_id', 'incident_count', 'risk_level', 'last_computed'),
  )
  return HttpResponse(data, content_type='application/json')


# API: Returns observation points as valid GeoJSON
def sightings_geojson(request):
  data = serialize(
      'geojson',
      WildlifeSighting.objects.all()[:250],
      geometry_field='location',
      fields=('species', 'common_name', 'observed_at', 'source', 'image_url'),
  )
  return HttpResponse(data, content_type='application/json')


# Dashboard Template View
def dashboard_view(request):
  total_sightings = WildlifeSighting.objects.count()
  total_hotspots = ConflictHotspot.objects.count()
  high_risk_count = ConflictHotspot.objects.filter(risk_level='high').count()

  context = {
      'total_sightings': total_sightings,
      'total_hotspots': total_hotspots,
      'high_risk_count': high_risk_count,
  }
  return render(request, 'wildlife/dashboard.html', context)