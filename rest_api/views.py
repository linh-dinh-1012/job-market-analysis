from django.shortcuts import render

from rest_framework.generics import ListAPIView
from .models import JobOffer
from .serializers import JobOfferSerializer

class JobOfferListView(ListAPIView):
    queryset = JobOffer.objects.all().order_by("-date_posted")
    serializer_class = JobOfferSerializer