import pytest

from apps.products.models import Category, ProductGroup, ProductSpec, ProductVariant


@pytest.mark.django_db
def test_category_str():
    cat = Category.objects.create(name="КТ", slug="kt")
    assert "КТ" in str(cat)


@pytest.mark.django_db
def test_category_tree_path():
    root = Category.objects.create(name="Root", slug="root")
    child = Category.objects.create(name="Child", slug="child", parent=root)
    ancestors = list(child.get_ancestors(include_self=True))
    assert len(ancestors) == 2


@pytest.mark.django_db
def test_product_group_slug_unique():
    cat = Category.objects.create(name="C", slug="c")
    ProductGroup.objects.create(name="G1", slug="g1", category=cat, product_type="KT")
    with pytest.raises(Exception):
        ProductGroup.objects.create(name="G2", slug="g1", category=cat, product_type="KT")


@pytest.mark.django_db
def test_variant_default_flag():
    cat = Category.objects.create(name="C", slug="c")
    group = ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT")
    v1 = ProductVariant.objects.create(group=group, sku_code="A", slug="a", execution="B", price=1, is_default=True)
    v2 = ProductVariant.objects.create(group=group, sku_code="B", slug="b", execution="B", price=2)
    assert v1.is_default is True
    assert v2.is_default is False


@pytest.mark.django_db
def test_product_spec_filterable():
    cat = Category.objects.create(name="C", slug="c")
    group = ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT")
    spec = ProductSpec.objects.create(group=group, spec_key="current", spec_value="400", filterable=True)
    assert spec.filterable is True


@pytest.mark.django_db
def test_inactive_group_hidden_from_active_filter():
    cat = Category.objects.create(name="C", slug="c")
    ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT", is_active=False)
    assert ProductGroup.objects.filter(is_active=True).count() == 0


@pytest.mark.django_db
def test_category_sort_order():
    c1 = Category.objects.create(name="B", slug="b", sort_order=2)
    c2 = Category.objects.create(name="A", slug="a", sort_order=1)
    ordered = list(Category.objects.order_by("sort_order", "name"))
    assert ordered[0].pk == c2.pk


@pytest.mark.django_db
def test_product_group_series_code():
    cat = Category.objects.create(name="C", slug="c")
    group = ProductGroup.objects.create(
        name="G", slug="g", category=cat, product_type="KT", series_code="6043",
    )
    assert group.series_code == "6043"


@pytest.mark.django_db
def test_variant_sku_unique():
    cat = Category.objects.create(name="C", slug="c")
    group = ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT")
    ProductVariant.objects.create(group=group, sku_code="UNIQ", slug="u1", execution="B", price=1)
    with pytest.raises(Exception):
        ProductVariant.objects.create(group=group, sku_code="UNIQ", slug="u2", execution="B", price=2)
