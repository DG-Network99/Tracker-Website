# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from django.views.generic import RedirectView

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    # path('notifications/<str:id>$', RedirectView.as_view(url = 'notifications/<str:id>/')),
    # path('notifications/<str:id>/', views.notifications, name='notifications'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
