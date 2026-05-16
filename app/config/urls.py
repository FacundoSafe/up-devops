from django.urls import path, include

urlpatterns = [
    path("api/cotizaciones/", include("routes.cotizaciones")),
    path("api/health/", include("routes.health")),
]
