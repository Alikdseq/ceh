"""Fallback SEO meta templates for catalog entities."""

from apps.products.models import Category, ProductGroup


def category_meta_title(name: str) -> str:
    return f"{name} — купить от производителя | Электроконтактор"


def category_meta_description(name: str) -> str:
    return (
        f"{name}: цены, характеристики, документация. "
        "Прямые поставки с завода во Владикавказе."
    )


def product_meta_title(name: str) -> str:
    return f"{name} — характеристики, цена | Купить у производителя"


def product_meta_description(group: ProductGroup) -> str:
    parts = [group.name]
    if group.nominal_current_a:
        parts.append(f"{group.nominal_current_a}А")
    if group.poles:
        parts.append(f"{group.poles} полюса")
    desc = ". ".join(parts)
    price = group.price_from
    if price and price > 0:
        desc += f". Цена от {price} ₽"
    desc += ". Паспорт, чертежи, заявка на поставку."
    return desc


def apply_category_meta(category: Category, overwrite: bool = False) -> bool:
    changed = False
    title = category_meta_title(category.name)
    description = category_meta_description(category.name)
    if overwrite or not category.meta_title:
        if category.meta_title != title:
            category.meta_title = title
            changed = True
    if overwrite or not category.meta_description:
        if category.meta_description != description:
            category.meta_description = description
            changed = True
    if changed:
        category.save(update_fields=["meta_title", "meta_description"])
    return changed


def apply_product_meta(group: ProductGroup, overwrite: bool = False) -> bool:
    changed = False
    title = product_meta_title(group.name)
    description = product_meta_description(group)
    if overwrite or not group.meta_title:
        if group.meta_title != title:
            group.meta_title = title
            changed = True
    if overwrite or not group.meta_description:
        if group.meta_description != description:
            group.meta_description = description
            changed = True
    if changed:
        group.save(update_fields=["meta_title", "meta_description"])
    return changed
