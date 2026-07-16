from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0003_productgroup_search_vector"),
    ]

    operations = [
        migrations.AddField(
            model_name="productgroup",
            name="image_rotation",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="Поворот фото на сайте: 0, 90, 180 или 270 градусов.",
                verbose_name="Поворот фото (градусы)",
            ),
        ),
    ]
