import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from notifications.cron import prepare_todos

if __name__ == '__main__':
    prepare_todos()
