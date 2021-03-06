# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.defaultfilters import slugify as django_slugify
try:
    from importlib import import_module
except ImportError:  # Django <= 1.8
    from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from unidecode import unidecode
from settings import EXTRA_FIELDS, RULES_PATH
from json import loads


# Timezone support with fallback.
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now


def slugify(s):
    """
    Translates unicode into closest possible ascii chars before
    slugifying.
    """
    from future.builtins import str
    return django_slugify(unidecode(str(s)))


def unique_slug(manager, slug_field, slug):
    """
    Ensure slug is unique for the given manager, appending a digit
    if it isn't.
    """
    i = 0
    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            slug = "%s-%s" % (slug, i)
        if not manager.filter(**{slug_field: slug}):
            break
        i += 1
    return slug


def split_choices(choices_string):
    """
    Convert a comma separated choices string to a list.
    """
    return [x.strip() for x in choices_string.split(",") if x.strip()]


def html5_field(name, base):
    """
    Takes a Django form field class and returns a subclass of
    it with the given name as its input type.
    """
    return type(str(""), (base,), {"input_type": name})


def import_attr(path):
    """
    Given a a Python dotted path to a variable in a module,
    imports the module and returns the variable in it.
    """
    module_path, attr_name = path.rsplit(".", 1)
    return getattr(import_module(module_path), attr_name)


def import_rule(slug):
    if RULES_PATH is None:
        raise ImproperlyConfigured(
            "You need to set the FORMS_BUILDER_RULES_PATH setting")
    module_path = ".".join([RULES_PATH, slug])

    try:
        return getattr(import_module(module_path), 'run')
    except ImportError:
        return None
    except AttributeError:
        raise ImproperlyConfigured(
            "You need to create a run() function in file %s.py" % module_path)


def get_templates_choices():
    return [(slugify(key), key) for key in EXTRA_FIELDS.keys()]


# def parse_choices(choices):
#     """
#     Iterator that takes a string of comma-separated JSON-formatted 
#     choices and yields each choice as a dictionnary
#     """
#     choice = ""
#     quoted = False
#     for char in choices[1:-1]:
#         if not quoted and char == '{':
#             quoted = True
#             choice += char
#         elif quoted and char == '}':
#             quoted = False
#             choice += char
#         elif char == "," and not quoted:
#             choice = choice.strip()
#             if choice:
#                 yield loads(choice)
#             choice = ""
#         else:
#             choice += char
#     choice = choice.strip()
#     if choice:
#         yield loads(choice)


def get_form_conf_for(template_slug):
    for slug, name in get_templates_choices():
        if slug == template_slug:
            return EXTRA_FIELDS[name]
    return {}
