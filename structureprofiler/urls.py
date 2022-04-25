"""structureprofiler url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from structureprofiler import views

urlpatterns = [
    path('', views.StructureProfilerView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.StructureProfilerJobViewSet)
router.register('output', views.StructureProfilerOutputViewSet)
urlpatterns.extend(router.urls)
