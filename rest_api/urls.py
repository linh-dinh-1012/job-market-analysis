from django.urls import path
from .views import JobOfferListView

urlpatterns = [
    path("jobs/", JobOfferListView.as_view(), name="jobs-list"),
]