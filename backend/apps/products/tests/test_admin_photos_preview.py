import pytest
from django.core.files.base import ContentFile

from apps.products.admin import ProductGroupAdmin
from apps.products.models import Category, ProductGroup, ProductImage


@pytest.mark.django_db
def test_photos_preview_with_existing_file_does_not_raise():
    cat = Category.objects.create(name="КТ", slug="kt-photos-preview")
    group = ProductGroup.objects.create(
        name="КТ6634",
        slug="kt6634-preview",
        category=cat,
        product_type="KT",
        series_code="6634",
    )
    img = ProductImage(group=group, is_primary=True, sort_order=0)
    img.image.save("kt6634_test.png", ContentFile(b"\x89PNG\r\n\x1a\n"), save=True)

    admin = ProductGroupAdmin(ProductGroup, None)
    html = str(admin.photos_preview(group))
    assert "Всего:" in html
    assert "figure" in html


@pytest.mark.django_db
def test_photos_preview_broken_files_only_shows_message():
    cat = Category.objects.create(name="КТ", slug="kt-photos-broken")
    group = ProductGroup.objects.create(
        name="КТ6634",
        slug="kt6634-broken",
        category=cat,
        product_type="KT",
    )
    ProductImage.objects.create(group=group, image="products/does_not_exist.png")

    admin = ProductGroupAdmin(ProductGroup, None)
    html = str(admin.photos_preview(group))
    assert "файлы на диске отсутствуют" in html
