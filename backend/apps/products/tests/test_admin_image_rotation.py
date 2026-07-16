import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.products.models import Category, ProductGroup


@pytest.mark.django_db
def test_admin_rotate_image_clockwise(client):
    user = get_user_model().objects.create_superuser("admin", "admin@test.local", "pass")
    client.force_login(user)
    cat = Category.objects.create(name="КТ", slug="kt-test-rotate")
    group = ProductGroup.objects.create(
        name="КТ 6043Б",
        slug="kt-6043-rotate-test",
        category=cat,
        product_type="KT",
        image_rotation=0,
    )
    url = reverse("admin:products_productgroup_rotate_image", args=[group.pk])
    response = client.get(f"{url}?dir=cw")
    assert response.status_code == 302
    group.refresh_from_db()
    assert group.image_rotation == 90
    client.get(f"{url}?dir=cw")
    group.refresh_from_db()
    assert group.image_rotation == 180
    client.get(f"{url}?dir=ccw")
    group.refresh_from_db()
    assert group.image_rotation == 90
    client.get(f"{url}?dir=reset")
    group.refresh_from_db()
    assert group.image_rotation == 0


@pytest.mark.django_db
def test_admin_product_change_with_missing_image_file(client):
    from apps.products.models import ProductImage

    user = get_user_model().objects.create_superuser("admin2", "a2@test.local", "pass")
    client.force_login(user)
    cat = Category.objects.create(name="КТ", slug="kt-admin-6634")
    group = ProductGroup.objects.create(
        name="КТ6634",
        slug="kt6634-admin-test",
        category=cat,
        product_type="KT",
        series_code="6634",
    )
    ProductImage.objects.create(
        group=group,
        image="products/kt6634_missing.png",
        is_primary=True,
    )

    change_url = reverse("admin:products_productgroup_change", args=[group.pk])
    response = client.get(change_url)
    assert response.status_code == 200
