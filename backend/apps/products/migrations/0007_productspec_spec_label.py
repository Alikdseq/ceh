from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_reset_image_rotation"),
    ]

    operations = [
        migrations.AddField(
            model_name="productspec",
            name="spec_label",
            field=models.CharField(
                blank=True,
                help_text="Если пусто — используется стандартное название параметра.",
                max_length=255,
                verbose_name="Название на сайте",
            ),
        ),
    ]
