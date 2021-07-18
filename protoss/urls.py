"""protoss url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from protoss import views

urlpatterns = [
    path('', views.ProtossView.as_view()),
]

router = DefaultRouter()
router.register('jobs', views.ProtossJobViewSet)
urlpatterns.extend(router.urls)
