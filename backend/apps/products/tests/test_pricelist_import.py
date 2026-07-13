import pytest
from django.core.management import call_command

from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.mark.django_db
def test_import_pricelist_keeps_kt_and_ktp_separate(tmp_path):
    Category.objects.create(name="КТ", slug="kt-6000b", parent=None)
    Category.objects.create(name="КТП 6000", slug="ktp-6000b", parent=None)

    csv_path = tmp_path / "pricelist.csv"
    csv_path.write_text(
        "category,sku_name,price_rub,nominal_current_a,product_type,notes\n"
        "Контакторы,КТ 6012Б (100А),10000,100,KT,\n"
        "Контакторы,КТП 6012Б (100А),10535,100,KTP,\n",
        encoding="utf-8",
    )

    call_command("import_pricelist", str(csv_path))

    kt = ProductGroup.objects.get(product_type="KT", series_code="6012")
    ktp = ProductGroup.objects.get(product_type="KTP", series_code="6012")
    assert kt.slug != ktp.slug
    assert kt.slug == "kontaktor-kt-6012-100a-b"
    assert ktp.slug == "kontaktor-ktp-6012-100a-b"
    assert kt.category.slug == "kt-6000b"
    assert ktp.category.slug == "ktp-6000b"

    kt_var = ProductVariant.objects.get(sku_code="КТ6012Б-У3")
    ktp_var = ProductVariant.objects.get(sku_code="КТП6012Б-У3")
    assert kt_var.group_id == kt.id
    assert ktp_var.group_id == ktp.id
