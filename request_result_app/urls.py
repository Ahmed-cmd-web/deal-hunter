from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"request", views.RequestViewSet, "request")
router.register(r"result", views.ResultViewSet, "result")
urlpatterns = router.urls
