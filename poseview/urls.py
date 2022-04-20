"""Poseview url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from poseview import views

urlpatterns = [
    path('', views.PoseviewView.as_view()),
]

router = DefaultRouter()
router.register('jobs', views.PoseviewJobViewSet)
urlpatterns.extend(router.urls)
