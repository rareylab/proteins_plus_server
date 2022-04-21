"""siena url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from siena import views

urlpatterns = [
    path('', views.SienaView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.SienaJobViewSet)
router.register('info', views.SienaInfoViewSet)
urlpatterns.extend(router.urls)
