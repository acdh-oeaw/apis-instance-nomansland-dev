# Generated by Django 4.2.15 on 2024-08-28 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apis_ontology", "0006_scripttype_alter_expression_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="expression",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="manuscript",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="manuscriptpart",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="person",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="place",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionevent",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionexpression",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versioninstitution",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionmanuscript",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionmanuscriptpart",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionperson",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionplace",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="versionwork",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="work",
            name="pk_old",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]