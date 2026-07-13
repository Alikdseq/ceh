from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0003_pricelist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="phone_sales",
            field=models.CharField(blank=True, max_length=80, verbose_name="Отдел сбыта"),
        ),
    ]
