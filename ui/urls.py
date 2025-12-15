from django.urls import path
from . import views

urlpatterns = [
    # Ruta vacía -> Muestra el Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # BORRA O COMENTA ESTA LÍNEA (ya no usamos API, el view hace todo):
    # path('api/predict/', views.api_predict, name='api_prediccion'),
]