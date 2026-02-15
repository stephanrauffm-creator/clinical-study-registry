from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, ProgrammingError


class Command(BaseCommand):
    help = "Create or reset local demo users for quick login testing"

    def handle(self, *args, **options):
        created = []
        updated = []

        try:
            basic_user, basic_created = User.objects.get_or_create(
                username="demo_user",
                defaults={"is_staff": False, "is_superuser": False, "is_active": True},
            )
            basic_user.set_password("DemoUser2026!")
            basic_user.is_staff = False
            basic_user.is_superuser = False
            basic_user.is_active = True
            basic_user.save(update_fields=["password", "is_staff", "is_superuser", "is_active"])
            (created if basic_created else updated).append("demo_user")

            admin_user, admin_created = User.objects.get_or_create(
                username="demo_admin",
                defaults={"is_staff": True, "is_superuser": True, "is_active": True},
            )
            admin_user.set_password("DemoAdmin2026!")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save(update_fields=["password", "is_staff", "is_superuser", "is_active"])
            (created if admin_created else updated).append("demo_admin")
        except (OperationalError, ProgrammingError) as exc:
            raise CommandError(
                "Database is not ready yet. Run `python manage.py migrate` first, then run `python manage.py create_demo_users`."
            ) from exc

        self.stdout.write(self.style.SUCCESS("Demo accounts are ready."))
        self.stdout.write(f"Created: {', '.join(created) if created else '-'}")
        self.stdout.write(f"Updated: {', '.join(updated) if updated else '-'}")
