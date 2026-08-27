from django.db import migrations


def reset_rotation(apps, schema_editor):
    ProductGroup = apps.get_model("products", "ProductGroup")
    ProductGroup.objects.exclude(image_rotation=0).update(image_rotation=0)


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0005_seo_models"),
    ]

    operations = [
        migrations.RunPython(reset_rotation, migrations.RunPython.noop),
    ]
