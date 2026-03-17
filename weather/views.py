from requests import RequestException
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .services import fetch_weather


def home(request):
    return render(request, "weather/index.html")


@require_GET
def get_weather(request):
    city = request.GET.get("city", "").strip()
    if not city:
        return JsonResponse({"error": "City is required."}, status=400)

    try:
        data = fetch_weather(city)
        return JsonResponse(data)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except RequestException:
        return JsonResponse({"error": "Weather provider is unavailable right now. Please try again."}, status=503)
    except Exception:
        return JsonResponse({"error": "Unexpected server error. Please try again later."}, status=500)
