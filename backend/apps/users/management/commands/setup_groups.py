from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


GROUPS = {
    "SuperAdmin": {"description": "Полный доступ"},
    "ContentManager": {"description": "Контент и каталог"},
    "SalesManager": {"description": "Заявки и лиды"},
    "ReadOnly": {"description": "Только просмотр"},
}


class Command(BaseCommand):
    help = "Create default user groups (STEP-022)"

    def handle(self, *args, **options):
        for name, meta in GROUPS.items():
            group, created = Group.objects.get_or_create(name=name)
            status = "created" if created else "exists"
            self.stdout.write(self.style.SUCCESS(f"Group {name}: {status} — {meta['description']}"))

        self.stdout.write(self.style.SUCCESS("Done: 4 groups ready"))
