from django.urls import path  # type: ignore
from . import views

# blog 
urlpatterns = [
    path('', views.index)
]