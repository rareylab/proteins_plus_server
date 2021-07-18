"""molecule_handler url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from molecule_handler import views

urlpatterns = [
    path('upload/', views.ProteinUploadView.as_view())
]

router = DefaultRouter()
router.register('proteins', views.ProteinViewSet)
router.register('ligands', views.LigandViewSet)
router.register('electron_density_maps', views.ElectronDensityMapViewSet)
router.register('upload/jobs', views.PreprocessorJobViewSet)
urlpatterns.extend(router.urls)
