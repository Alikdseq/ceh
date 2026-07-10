from django.db import migrations, models


def create_productgroup_search_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS products_productgroup_search_vector_gin
            ON products_productgroup USING gin (search_vector gin_trgm_ops)
            """
        )


def drop_productgroup_search_index(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS products_productgroup_search_vector_gin")


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_search_trigram_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="productgroup",
            name="search_vector",
            field=models.TextField(blank=True, editable=False, verbose_name="Search index"),
        ),
        migrations.RunPython(create_productgroup_search_index, drop_productgroup_search_index),
    ]
