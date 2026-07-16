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
