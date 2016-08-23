from django.conf import settings

from . import DEFAULTS


def get_config(name):
    return getattr(settings, name, DEFAULTS[name])
