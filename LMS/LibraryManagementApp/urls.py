from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.login, name="login"),
]
