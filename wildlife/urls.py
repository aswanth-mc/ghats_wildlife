from django.urls import path
from wildlife import views

app_name = 'wildlife'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/hotspots/', views.hotspots_geojson, name='hotspots_api'),
    path('api/sightings/', views.sightings_geojson, name='sightings_api'),
]