# Generated by Django 4.2.13 on 2024-06-25 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "request_result_app",
            "0002_result_discounted_price_alter_result_original_price_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="request",
            name="requested_count",
            field=models.IntegerField(default=0),
        ),
    ]
