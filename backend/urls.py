"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from backend.app import views
from backend.app import api
from backend.app import api_more


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome),
    path('api/health/', api.health, name='api-health'),
    path('api/signup/', api.signup, name='api-signup'),
    path('api/login/', api.login, name='api-login'),
    path('api/logout/', api.logout, name='api-logout'),
    path('api/me/', api.me, name='api-me'),
    path('api/stops/nearby/', api.nearby_stops, name='api-stops-nearby'),
    path('api/map/', api.map_layer, name='api-map'),
    path('api/fares/', api.fares, name='api-fares'),
    path('api/purchase/', api.purchase, name='api-purchase'),
    path('api/alerts/', api_more.alerts, name='api-alerts'),
    path('api/trips/', api_more.trips, name='api-trips'),
    path('api/reports/', api_more.report_issue, name='api-report-issue'),
    path('api/admin/summary/', api_more.admin_summary, name='api-admin-summary'),
    path('api/admin/reports/', api_more.admin_reports, name='api-admin-reports'),
    path('api/admin/alerts/', api_more.admin_create_alert, name='api-admin-create-alert'),
]
