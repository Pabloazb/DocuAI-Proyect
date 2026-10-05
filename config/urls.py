from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.inicio, name="inicio"),
    path("explicacion/",views.explicacion,name="explicacion",),
    path("registro/",views.registro,name="registro",),
    path("login/",auth_views.LoginView.as_view( template_name="clasificador/login.html" ), name="login",),
    path("logout/",auth_views.LogoutView.as_view(),name="logout",),
    path("resultado/",views.resultado_json,name="resultado_json",),
    
]