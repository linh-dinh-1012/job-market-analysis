from rest_framework import serializers
from .models import JobOffer


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = [
            "id",
            "title",
            "description",
            "salary_min_annual",
            "salary_max_annual",
            "experience",
            "education",
            "date_posted",
            "url",
            "contract_id",
            "company_id",
            "industry_id",
            "location_id",
        ]