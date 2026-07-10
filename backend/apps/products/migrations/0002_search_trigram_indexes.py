from django.db import migrations


def enable_trigram(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")


def create_gin_indexes(apps, schema_editor):
    """Indexes only for columns that exist after 0001_initial.

    ProductGroup.search_vector is added in 0003 — its GIN index is created there.
    """
    if schema_editor.connection.vendor != "postgresql":
        return
    statements = [
        """
        CREATE INDEX IF NOT EXISTS products_productgroup_series_code_gin
        ON products_productgroup USING gin (series_code gin_trgm_ops)
        """,
        """
        CREATE INDEX IF NOT EXISTS products_productvariant_search_vector_gin
        ON products_productvariant USING gin (search_vector gin_trgm_ops)
        """,
        """
        CREATE INDEX IF NOT EXISTS products_productvariant_sku_code_gin
        ON products_productvariant USING gin (sku_code gin_trgm_ops)
        """,
    ]
    with schema_editor.connection.cursor() as cursor:
        for sql in statements:
            cursor.execute(sql)


def drop_gin_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    names = [
        "products_productgroup_series_code_gin",
        "products_productvariant_search_vector_gin",
        "products_productvariant_sku_code_gin",
    ]
    with schema_editor.connection.cursor() as cursor:
        for name in names:
            cursor.execute(f"DROP INDEX IF EXISTS {name}")


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(enable_trigram, migrations.RunPython.noop),
        migrations.RunPython(create_gin_indexes, drop_gin_indexes),
    ]
