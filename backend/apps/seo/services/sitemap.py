from xml.etree.ElementTree import Element, SubElement, tostring

from django.conf import settings
from django.utils import timezone

from apps.content.models import CaseStudy, CityCategoryLanding, DeliveryCity, NewsPost, Page
from apps.products.models import Category, ProductGroup
from apps.products.utils import category_path_slugs, get_public_category_ids, is_category_public, product_catalog_path
from apps.seo.application_landings import APPLICATION_LANDING_SLUGS


STATIC_PATHS = [
    ("/", "1.0", "weekly"),
    ("/catalog/", "0.8", "weekly"),
    ("/pricelist/", "0.8", "weekly"),
    ("/about/", "0.7", "monthly"),
    ("/about/production/", "0.7", "monthly"),
    ("/about/certificates/", "0.7", "monthly"),
    ("/contacts/", "0.7", "monthly"),
    ("/support/", "0.7", "monthly"),
    ("/dealers/", "0.7", "monthly"),
    ("/partners/", "0.6", "monthly"),
    ("/shareholders/", "0.5", "monthly"),
    ("/news/", "0.6", "weekly"),
    ("/cases/", "0.7", "monthly"),
    ("/delivery/", "0.6", "monthly"),
    ("/privacy/", "0.3", "yearly"),
    ("/terms/", "0.3", "yearly"),
    ("/applications/", "0.7", "monthly"),
]

for _slug in APPLICATION_LANDING_SLUGS:
    STATIC_PATHS.append((f"/applications/{_slug}/", "0.7", "monthly"))


def _base_url() -> str:
    return getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")


def _date_iso(dt) -> str:
    if dt is None:
        return timezone.now().date().isoformat()
    if hasattr(dt, "date"):
        return dt.date().isoformat()
    return str(dt)


def _category_url_path(category) -> str:
    slugs = category_path_slugs(category)
    return f"/catalog/{'/'.join(slugs)}"


def collect_urls() -> list[dict]:
    base = _base_url()
    now = timezone.now().date().isoformat()
    urls: list[dict] = []

    for path, priority, changefreq in STATIC_PATHS:
        urls.append({
            "loc": f"{base}{path}",
            "lastmod": now,
            "changefreq": changefreq,
            "priority": priority,
        })

    for cat in Category.objects.filter(is_active=True):
        if not is_category_public(cat):
            continue
        path = _category_url_path(cat)
        lastmod = _date_iso(getattr(cat, "updated_at", None))
        urls.append({
            "loc": f"{base}{path}",
            "lastmod": lastmod,
            "changefreq": "weekly",
            "priority": "0.8",
        })

    public_ids = get_public_category_ids()
    for group in ProductGroup.objects.filter(is_active=True, category_id__in=public_ids).select_related("category"):
        path = product_catalog_path(group)
        urls.append({
            "loc": f"{base}{path}",
            "lastmod": _date_iso(group.updated_at),
            "changefreq": "weekly",
            "priority": "0.9",
        })

    for post in NewsPost.objects.filter(is_published=True):
        lastmod = _date_iso(post.updated_at if hasattr(post, "updated_at") else post.published_at)
        urls.append({
            "loc": f"{base}/news/{post.slug}",
            "lastmod": lastmod,
            "changefreq": "monthly",
            "priority": "0.6",
        })

    seen_locs = {u["loc"] for u in urls}
    for page in Page.objects.filter(is_published=True):
        slug_map = {
            "about": "/about",
            "contacts": "/contacts",
            "privacy": "/privacy",
            "terms": "/terms",
            "support": "/support",
            "dealers": "/dealers",
            "about-production": "/about/production",
            "about-certificates": "/about/certificates",
        }
        path = slug_map.get(page.slug, f"/pages/{page.slug}")
        loc = f"{base}{path}"
        if loc in seen_locs:
            continue
        seen_locs.add(loc)
        urls.append({
            "loc": loc,
            "lastmod": _date_iso(page.updated_at),
            "changefreq": "monthly",
            "priority": "0.5",
        })

    for study in CaseStudy.objects.filter(is_published=True):
        urls.append({
            "loc": f"{base}/cases/{study.slug}/",
            "lastmod": _date_iso(study.updated_at),
            "changefreq": "monthly",
            "priority": "0.6",
        })

    for city in DeliveryCity.objects.filter(is_indexable=True):
        urls.append({
            "loc": f"{base}/delivery/{city.slug}/",
            "lastmod": _date_iso(city.updated_at),
            "changefreq": "monthly",
            "priority": "0.5",
        })

    for landing in CityCategoryLanding.objects.filter(is_indexable=True).select_related("city", "category"):
        urls.append({
            "loc": f"{base}/delivery/{landing.city.slug}/{landing.category.slug}/",
            "lastmod": _date_iso(landing.updated_at),
            "changefreq": "monthly",
            "priority": "0.5",
        })

    return urls


def build_sitemap_xml() -> bytes:
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for item in collect_urls():
        url_el = SubElement(urlset, "url")
        SubElement(url_el, "loc").text = item["loc"]
        SubElement(url_el, "lastmod").text = item["lastmod"]
        SubElement(url_el, "changefreq").text = item["changefreq"]
        SubElement(url_el, "priority").text = item["priority"]
    return tostring(urlset, encoding="utf-8", xml_declaration=True)


def build_robots_txt() -> str:
    base = _base_url()
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /manage/\n"
        "Disallow: /api/\n"
        "Disallow: /cart\n"
        "Disallow: /compare\n"
        "Disallow: /order/\n"
        "Disallow: /search\n"
        "Disallow: /subscribe/confirm/\n"
        "Disallow: /unsubscribe/\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


def write_sitemap_file() -> str:
    path = settings.MEDIA_ROOT / "sitemap.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_sitemap_xml())
    return str(path)
