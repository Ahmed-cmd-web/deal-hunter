# Generated by Django 4.2.13 on 2024-06-26 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_result_app", "0004_request_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="result",
            name="percentage",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="request",
            name="source_country",
            field=models.CharField(
                choices=[
                    (
                        "{'name': 'Egypt', 'code': 'EG', 'flag': '🇪🇬', 'currency': 'egp'}",
                        "Egypt",
                    )
                ],
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="request",
            name="target_country",
            field=models.CharField(
                choices=[
                    (
                        "{'name': 'Saudi Arabia', 'code': 'SA', 'flag': '🇸🇦', 'currency': 'sar'}",
                        "Ksa",
                    ),
                    (
                        "{'name': 'United Arab Emirates', 'code': 'AE', 'flag': '🇦🇪', 'currency': 'aed'}",
                        "Uae",
                    ),
                ],
                max_length=255,
            ),
        ),
    ]
