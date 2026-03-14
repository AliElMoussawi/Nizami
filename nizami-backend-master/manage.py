#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Python 3.12+ no longer bundles pkg_resources; django-q expects it. Provide a shim using stdlib.
if sys.version_info >= (3, 12) and "pkg_resources" not in sys.modules:
    import importlib.metadata
    import types

    def _iter_entry_points(group, name=None):
        for ep in importlib.metadata.entry_points().select(group=group):
            if name is None or ep.name == name:
                yield ep

    _pkg_resources = types.ModuleType("pkg_resources")
    _pkg_resources.iter_entry_points = _iter_entry_points
    sys.modules["pkg_resources"] = _pkg_resources

from src.common.env_loader import load_env


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
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
    load_env()
    main()
