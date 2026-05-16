from dataclasses import asdict

from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from controllers.health import get_health


@api_view(["GET"])
def health_view(request):
    return Response(asdict(get_health()))


urlpatterns = [
    path("", health_view, name="health"),
]
