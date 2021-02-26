#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    # os.system("sudo python3 /home/pi/EnviroServ/getsensordata.py")
    # os.system("sudo python3 /home/pi/EnviroServ/getresources.py")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EnviroServ.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
