"""GeoMine URL definitions"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from geomine import views

urlpatterns = [
    path('', views.GeoMineView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.GeoMineJobViewSet)
router.register('info', views.GeoMineInfoViewSet)
urlpatterns.extend(router.urls)

