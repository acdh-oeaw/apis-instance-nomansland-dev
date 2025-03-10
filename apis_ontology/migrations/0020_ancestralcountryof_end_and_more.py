# Generated by Django 5.1.6 on 2025-02-22 23:17

import django_interval.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "apis_ontology",
            "0019_remove_person_end_remove_person_end_date_from_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="ancestralcountryof",
            name="end",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="end_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="end_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="end_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="start",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="start_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="start_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="ancestralcountryof",
            name="start_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="end",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="end_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="end_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="end_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="start",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="start_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="start_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionancestralcountryof",
            name="start_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
    ]
