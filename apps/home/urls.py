from django.urls import path, re_path
from apps.home import views
from django.views.generic import RedirectView

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('dashboard', views.main_dashboard, name='main_dashboard'),
    path('notification_update', views.notification_update, name='notification_update'),
    path('track', views.track, name='track'),
    path('stop_track', views.stop_track, name='stop_track'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('about_us', views.about_us, name='about_us'),
    # path('products', views.products, name='products'),
    # path('notifications/<str:id>$', RedirectView.as_view(url = 'notifications/<str:id>/')),
    # path('notifications/<str:id>/', views.notifications, name='notifications'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
