from dataclasses import asdict

from django.urls import path
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from controllers.cotizaciones import get_cotizaciones


@api_view(["GET"])
def cotizaciones_view(request):
    try:
        return Response(asdict(get_cotizaciones()))
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response(
            {"error": "Error al obtener cotizaciones del BNA", "detalle": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


urlpatterns = [
    path("", cotizaciones_view, name="cotizaciones"),
]
