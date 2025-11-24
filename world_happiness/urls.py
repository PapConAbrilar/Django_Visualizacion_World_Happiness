from django.urls import path
from . import views
urlpatterns = [
    path('index/', views.index, name='index'),
    path('happiness/', views.happiness, name='happiness'),
    path('economy/', views.economy, name='economy'),
    path('trust/', views.trust, name='trust'),
    path('generosity_freedom/', views.generosity_freedom, name='generosity_freedom'),
    path('mapa_mundi/', views.mapa_mundi, name='mapa_mundi'),
    path('agregar_pais/', views.agregar_pais, name="agregar_pais"),
    path('agregar_pais_csv/', views.agregar_pais_csv, name="agregar_pais_csv"),
    path('dashboard/', views.dashboard_interactivo, name='dashboard')
]