# Generated by Django 4.2.13 on 2024-06-26 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_result_app", "0003_request_requested_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="request",
            name="price",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
