from django.shortcuts import render
from django.http import JsonResponse
from .ai_brain import predecir_precio_futuro # Importamos el cerebro que acabas de mover

# 1. Vista del Panel (Dashboard)
def dashboard(request):
    return render(request, 'ui/dashboard.html')

# 2. Vista de la API (La que consulta el JS)
def api_prediccion(request):
    try:
        # Llamamos al cerebro
        resultado = predecir_precio_futuro()
        return JsonResponse(resultado)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)