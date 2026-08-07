import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse

from apps.products.admin import ProductGroupAdmin, ProductSpecInline
from apps.products.admin_forms import ProductVariantAdminForm
from apps.products.models import Category, ProductGroup, ProductSpec, ProductVariant


@pytest.mark.django_db
def test_variant_admin_form_accepts_comma_decimal_price():
    cat = Category.objects.create(name="КТ", slug="kt-form-price")
    group = ProductGroup.objects.create(
        name="КТ6012Б",
        slug="kt6012b-form-price",
        category=cat,
        product_type="KT",
    )
    variant = ProductVariant.objects.create(
        group=group,
        sku_code="КТ6012Б-У3-220V",
        slug="kt6012b-u3-220v-form",
        execution="B",
        price="1000.00",
        is_default=True,
    )

    form = ProductVariantAdminForm(
        data={
            "sku_code": variant.sku_code,
            "execution": "B",
            "coil_voltage_v": "220",
            "aux_contacts": "",
            "price": "1 500,50",
            "stock_status": "in_stock",
            "is_active": "on",
        },
        instance=variant,
    )
    assert form.is_valid(), form.errors
    saved = form.save()
    assert saved.price == pytest.approx(1500.50)


@pytest.mark.django_db
def test_spec_inline_excludes_duplicate_nominal_current():
    cat = Category.objects.create(name="КТ", slug="kt-spec-inline")
    group = ProductGroup.objects.create(
        name="КТ6012Б",
        slug="kt6012b-spec-inline",
        category=cat,
        product_type="KT",
        nominal_current_a=12,
    )
    ProductSpec.objects.create(group=group, spec_key="nominal_current", spec_value="12", spec_unit="А")
    ProductSpec.objects.create(group=group, spec_key="frequency", spec_value="50", spec_unit="Гц")

    user = get_user_model().objects.create_superuser("inline-spec", "inline@test.local", "pass")
    inline = ProductSpecInline(ProductGroup, admin.site)
    request = RequestFactory().get("/")
    request.user = user
    qs = inline.get_queryset(request)
    keys = set(qs.values_list("spec_key", flat=True))
    assert "nominal_current" not in keys
    assert "frequency" in keys


@pytest.mark.django_db
def test_change_view_removes_legacy_nominal_current_spec():
    user = get_user_model().objects.create_superuser("admin-spec", "spec@test.local", "pass")
    cat = Category.objects.create(name="КТ", slug="kt-change-spec")
    group = ProductGroup.objects.create(
        name="КТ6012Б",
        slug="kt6012b-change-spec",
        category=cat,
        product_type="KT",
        nominal_current_a=12,
    )
    ProductSpec.objects.create(group=group, spec_key="nominal_current", spec_value="12", spec_unit="А")

    url = reverse("admin:products_productgroup_change", args=[group.pk])
    admin_instance = ProductGroupAdmin(ProductGroup, admin.site)
    request = RequestFactory().get(url)
    request.user = user
    response = admin_instance.change_view(request, str(group.pk))
    assert response.status_code == 200
    assert not ProductSpec.objects.filter(group=group, spec_key="nominal_current").exists()
