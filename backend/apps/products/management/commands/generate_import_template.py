from pathlib import Path

from django.core.management.base import BaseCommand
from openpyxl import Workbook


class Command(BaseCommand):
    help = "Generate Excel import template (STEP-024)"

    def handle(self, *args, **options):
        # backend/apps/products/management/commands -> project root is 5 levels up
        out_dir = Path(__file__).resolve().parents[5] / "data" / "templates"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "import_products.xlsx"

        wb = Workbook()

        sheets = {
            "categories": [
                "slug", "name", "parent_slug", "description", "meta_title",
                "meta_description", "h1", "sort_order", "is_active",
            ],
            "product_groups": [
                "slug", "name", "category_slug", "short_description", "series_code",
                "product_type", "nominal_current_a", "nominal_voltage_v", "poles",
                "application_category", "honest_sign", "meta_title", "is_active", "is_featured",
            ],
            "variants": [
                "sku_code", "slug", "group_slug", "execution", "coil_type",
                "coil_voltage_v", "aux_contacts", "price", "stock_status", "is_default", "is_active",
            ],
            "specs": [
                "group_slug", "spec_key", "spec_value", "spec_unit", "filterable", "sort_order",
            ],
        }

        first = True
        for sheet_name, headers in sheets.items():
            if first:
                ws = wb.active
                ws.title = sheet_name
                first = False
            else:
                ws = wb.create_sheet(sheet_name)
            ws.append(headers)
            if sheet_name == "variants":
                ws.append([
                    "KT6043B-U3", "kt6043b-u3", "kontaktor-kt-6043", "B", "AC",
                    "220", "2NO+2NC", "25100", "in_stock", "1", "1",
                ])

        wb.save(out_path)
        self.stdout.write(self.style.SUCCESS(f"Template saved: {out_path}"))
