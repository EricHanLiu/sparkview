import os
import django
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from notifications.cron import prepare_todos


def main():
    prepare_todos()


main()
