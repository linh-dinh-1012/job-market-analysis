from django.db import models

class JobOffer(models.Model):
    id = models.AutoField(primary_key=True)

    title = models.TextField()
    description = models.TextField(null=True)

    salary_min_annual = models.TextField(null=True)
    salary_max_annual = models.TextField(null=True)
    experience = models.TextField(null=True)
    education = models.TextField(null=True)

    date_posted = models.DateField(null=True)
    url = models.TextField(unique=True)

    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    contract_id = models.IntegerField(null=True)
    company_id = models.IntegerField(null=True)
    industry_id = models.IntegerField(null=True)
    location_id = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = "job_offer"