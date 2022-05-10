"""DoGSite URL definitions"""
from django.urls import path
from rest_framework.routers import DefaultRouter
from dogsite import views

urlpatterns = [
    path('', views.DoGSiteView.as_view())
]

router = DefaultRouter()
router.register('jobs', views.DoGSiteJobViewSet)
router.register('info', views.DoGSiteInfoViewSet)
urlpatterns.extend(router.urls)
