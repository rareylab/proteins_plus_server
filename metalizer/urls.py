"""Metalizer URL definitions"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from metalizer import views

urlpatterns = [
    path('', views.MetalizerView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.MetalizerJobViewSet)
router.register('info', views.MetalizerInfoViewSet)
urlpatterns.extend(router.urls)
