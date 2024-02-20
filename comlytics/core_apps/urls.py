from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('scanner/', views.scanner, name='scanner'),

]