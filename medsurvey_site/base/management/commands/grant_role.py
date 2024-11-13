from django.core.management.base import BaseCommand, CommandError
from base.models import UserAdditionalData
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "(NOT IMPLEMENTED!) Grant a role to user"

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)
        parser.add_argument("role", type=str)

    def handle(self, *args, **options):
        pass