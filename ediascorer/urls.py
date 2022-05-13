"""ediascorer url endpoints"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from ediascorer import views

urlpatterns = [
    path('', views.EdiascorerView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.EdiaJobViewSet)
router.register('scores', views.EdiaScoresViewSet)
urlpatterns.extend(router.urls)
