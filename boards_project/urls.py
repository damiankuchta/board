"""boards_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

import debug_toolbar

from django.urls import path, include

urlpatterns = [
    path('', include("boards_app.urls")),
    path('topic/', include("topics_app.urls")),
    path('user/', include("userprofiles_app.urls")),
    path('report/', include("reports_warrnings_bans_app.urls")),
    path('admin/', admin.site.urls, name="admin"),
    path('__debug__/', include(debug_toolbar.urls)),
]
