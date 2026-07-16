import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.products.models import Category, ProductGroup, ProductImage


@pytest.mark.django_db
def test_admin_change_ktp6623s_with_cyrillic_missing_file(client):
    user = get_user_model().objects.create_superuser("admin6623", "a6623@test.local", "pass")
    client.force_login(user)
    cat = Category.objects.create(name="КТП", slug="ktp-admin-6623")
    group = ProductGroup.objects.create(
        name="КТП6623С",
        slug="ktp6623s-admin",
        category=cat,
        product_type="KTP",
        series_code="6623",
        image_rotation=270,
    )
    ProductImage.objects.create(
        group=group,
        image="products/КТП6623С_uYlHGbe.png",
        is_primary=True,
    )

    url = reverse("admin:products_productgroup_change", args=[group.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert not ProductImage.objects.filter(group=group).exists()
