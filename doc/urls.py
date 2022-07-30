from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import DocViewSet

router = SimpleRouter()
router.register("doc", DocViewSet, basename="doc")

urlpatterns = (path("", include(router.urls)),)

