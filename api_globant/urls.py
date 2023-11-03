from django.urls import path
from . import views

urlpatterns = [
    path('quarters/', views.quarters),
    path('number_hires/', views.number_hires),
]