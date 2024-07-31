# Generated by Django 4.2.13 on 2024-07-31 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_result_app", "0006_alter_request_source_country_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="target_country",
            field=models.CharField(
                choices=[
                    (
                        "{'name': 'Saudi Arabia', 'code': 'KSA', 'flag': '🇸🇦', 'currency': 'sar'}",
                        "Ksa",
                    ),
                    (
                        "{'name': 'United Arab Emirates', 'code': 'UAE', 'flag': '🇦🇪', 'currency': 'aed'}",
                        "Uae",
                    ),
                    (
                        "{'name': 'Germany', 'code': 'DE', 'flag': '🇩🇪', 'currency': 'eur'}",
                        "De",
                    ),
                    (
                        "{'name': 'France', 'code': 'FR', 'flag': '🇫🇷', 'currency': 'eur'}",
                        "Fr",
                    ),
                    (
                        "{'name': 'Spain', 'code': 'ES', 'flag': '🇪🇸', 'currency': 'eur'}",
                        "Es",
                    ),
                    (
                        "{'name': 'Italy', 'code': 'IT', 'flag': '🇮🇹', 'currency': 'eur'}",
                        "It",
                    ),
                ],
                max_length=255,
            ),
        ),
    ]
