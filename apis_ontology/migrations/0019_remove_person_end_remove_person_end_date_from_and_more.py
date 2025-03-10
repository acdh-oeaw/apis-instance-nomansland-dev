# Generated by Django 5.1.5 on 2025-01-23 10:42

import django_interval.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apis_ontology", "0001_squashed_0018_merge_20250122_0916"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="person",
            name="end",
        ),
        migrations.RemoveField(
            model_name="person",
            name="end_date_from",
        ),
        migrations.RemoveField(
            model_name="person",
            name="end_date_sort",
        ),
        migrations.RemoveField(
            model_name="person",
            name="end_date_to",
        ),
        migrations.RemoveField(
            model_name="person",
            name="start",
        ),
        migrations.RemoveField(
            model_name="person",
            name="start_date_from",
        ),
        migrations.RemoveField(
            model_name="person",
            name="start_date_sort",
        ),
        migrations.RemoveField(
            model_name="person",
            name="start_date_to",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="end",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="end_date_from",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="end_date_sort",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="end_date_to",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="start",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="start_date_from",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="start_date_sort",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="start_date_to",
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_birth_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_birth_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_birth_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_death_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_death_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="date_of_death_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_birth_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_birth_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_birth_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_death_date_from",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_death_date_sort",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="date_of_death_date_to",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="date_of_birth",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="date_of_death",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="versionperson",
            name="date_of_birth",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="versionperson",
            name="date_of_death",
            field=django_interval.fields.FuzzyDateParserField(blank=True, null=True),
        ),
    ]
