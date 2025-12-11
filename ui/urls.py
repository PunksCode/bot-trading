from django.urls import path
from . import views

urlpatterns = [
    # Ruta vacía -> Muestra el Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Ruta /api/predict/ -> Llama a la IA
    path('api/predict/', views.api_prediccion, name='api_prediccion'),
]