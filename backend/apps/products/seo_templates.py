"""Fallback SEO meta templates for catalog entities."""

from django.utils.html import escape

from apps.products.models import Category, ProductGroup, ProductFAQ


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


def product_h1(group: ProductGroup) -> str:
    return group.h1 or group.name


def product_full_description_html(group: ProductGroup) -> str:
    name = escape(group.name)
    current = f"{group.nominal_current_a} А" if group.nominal_current_a else ""
    type_label = group.get_product_type_display()
    honest = (
        "<p>Продукция участвует в системе маркировки «Честный знак».</p>"
        if group.honest_sign
        else ""
    )
    return (
        f"<h2>Назначение</h2>"
        f"<p>{name} — {type_label.lower()} для коммутации силовых цепей "
        f"{'номинальным током ' + escape(current) + '. ' if current else ''}"
        f"Предназначен для установки в щитовое и промышленное оборудование.</p>"
        f"<h2>Преимущества</h2>"
        f"<ul>"
        f"<li>Прямые поставки с завода во Владикавказе, без посредников</li>"
        f"<li>Публичная цена производителя с НДС</li>"
        f"<li>Паспорт, чертежи и сертификаты доступны на сайте</li>"
        f"<li>Российское производство, сервисная поддержка</li>"
        f"</ul>"
        f"<h2>Область применения</h2>"
        f"<p>Используется в НКУ, крановом оборудовании, насосных станциях, "
        f"компрессорных установках и других объектах, где требуется надёжная коммутация нагрузки.</p>"
        f"{honest}"
        f"<h2>Документация</h2>"
        f"<p>На вкладке «Документация» карточки доступны типовые паспорта, габаритные чертежи "
        f"и инструкции по эксплуатации. Для коммерческого предложения оформите заявку в корзине.</p>"
    )


def default_product_faqs(group: ProductGroup) -> list[tuple[str, str]]:
    faqs = [
        (
            f"Как заказать {group.name}?",
            "Добавьте нужный вариант в корзину-заявку и отправьте форму — менеджер подготовит "
            "коммерческое предложение с актуальной ценой и сроками.",
        ),
        (
            "Цена указана с НДС?",
            "Да, на сайте публикуются цены производителя с учётом НДС согласно действующему прайс-листу.",
        ),
    ]
    if group.nominal_current_a:
        faqs.append(
            (
                f"Какой номинальный ток у {group.name}?",
                f"Номинальный рабочий ток — {group.nominal_current_a} А (см. таблицу характеристик).",
            ),
        )
    if group.honest_sign:
        faqs.append(
            (
                "Есть ли маркировка «Честный знак»?",
                "Да, данная серия участвует в обязательной маркировке «Честный знак».",
            ),
        )
    return faqs[:5]


def apply_product_seo_copy(group: ProductGroup, overwrite: bool = False) -> bool:
    """Meta, h1, full_description and default FAQ for PDP."""
    changed = False
    update_fields: list[str] = []

    title = product_meta_title(group.name)
    description = product_meta_description(group)
    if overwrite or not group.meta_title:
        if group.meta_title != title:
            group.meta_title = title
            update_fields.append("meta_title")
            changed = True
    if overwrite or not group.meta_description:
        if group.meta_description != description:
            group.meta_description = description
            update_fields.append("meta_description")
            changed = True

    h1 = group.name if (overwrite or not (group.h1 or "").strip()) else group.h1
    if group.h1 != h1:
        group.h1 = h1
        update_fields.append("h1")
        changed = True

    html = product_full_description_html(group)
    if overwrite or not (group.full_description or "").strip():
        if group.full_description != html:
            group.full_description = html
            update_fields.append("full_description")
            changed = True

    if update_fields:
        group.save(update_fields=update_fields)

    if overwrite or not group.faqs.exists():
        if overwrite:
            group.faqs.all().delete()
        if not group.faqs.exists():
            for idx, (q, a) in enumerate(default_product_faqs(group)):
                ProductFAQ.objects.create(group=group, question=q, answer=a, sort_order=idx)
            changed = True

    return changed
