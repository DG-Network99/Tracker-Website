from django.urls import path
from .views import login_view, register_user
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('login', login_view, name="login"),
    path('register', register_user, name="register"),
    path("logout", LogoutView.as_view(), name="logout"),

    # PASSWORD RESET CODE 
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),

]
