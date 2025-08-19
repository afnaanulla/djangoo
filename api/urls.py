from django.urls import path
from . import views

urlpatterns = [
    path('auth/csrf/', views.CSRF.as_view(), name="auth-csrf"),
    path('auth/login/', views.Login.as_view(), name="auth-login"),
    path('auth/logout/', views.Logout.as_view(), name="auth-logout"),
    path('auth/register/', views.Register.as_view(), name="auth-register"),
    path('auth/user/', views.UserView.as_view(), name="auth-user"),
    path('indicators/', views.Indicators.as_view(), name="indicators"),
]
