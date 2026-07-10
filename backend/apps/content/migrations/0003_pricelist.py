# Generated manually for price list models

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0002_newspost_newsletter_sent_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="PriceListSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Раздел")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
            ],
            options={
                "verbose_name": "Раздел прайс-листа",
                "verbose_name_plural": "Разделы прайс-листа",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="PriceListItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Наименование")),
                ("price", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="Цена, ₽")),
                ("nominal_current_a", models.PositiveIntegerField(blank=True, null=True, verbose_name="Ном. ток, А")),
                ("product_type", models.CharField(blank=True, max_length=20, verbose_name="Тип")),
                ("notes", models.CharField(blank=True, max_length=255, verbose_name="Примечание")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="content.pricelistsection",
                        verbose_name="Раздел",
                    ),
                ),
            ],
            options={
                "verbose_name": "Позиция прайс-листа",
                "verbose_name_plural": "Позиции прайс-листа",
                "ordering": ["section__sort_order", "sort_order", "name"],
            },
        ),
    ]
