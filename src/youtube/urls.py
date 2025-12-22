from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('api/summarize/', views.summarize_video, name='summarize_video'),
]