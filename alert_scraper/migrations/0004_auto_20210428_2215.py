# Generated by Django 3.1 on 2021-04-28 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alert_scraper', '0003_scrapedalert_alert_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapedalert',
            name='alert_data',
            field=models.FileField(null=True, upload_to='alerts'),
        ),
    ]