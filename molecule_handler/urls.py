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
router.register('protein_sites', views.ProteinSiteViewSet)
router.register('electron_density_maps', views.ElectronDensityMapViewSet)
router.register('job_data', views.PreprocessorJobDataViewSet)
router.register('upload/jobs', views.PreprocessorJobViewSet)
urlpatterns.extend(router.urls)
