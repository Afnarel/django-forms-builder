from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django import forms
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.settings import USE_HTML5, EXTRA_FIELDS
from forms_builder.forms.utils import html5_field, import_attr


# Constants for all available field types.
TEXT = 1
TEXTAREA = 2
EMAIL = 3
CHECKBOX = 4
CHECKBOX_MULTIPLE = 5
SELECT = 6
SELECT_MULTIPLE = 7
RADIO_MULTIPLE = 8
FILE = 9
DATE = 10
DATE_TIME = 11
HIDDEN = 12
NUMBER = 13
URL = 14
DOB = 15

# Names for all available field types.
NAMES = [
    (TEXT, _("Single line text")),
    (TEXTAREA, _("Multi line text")),
    (EMAIL, _("Email")),
    (NUMBER, _("Number")),
    (URL, _("URL")),
    (CHECKBOX, _("Check box")),
    (CHECKBOX_MULTIPLE, _("Check boxes")),
    (SELECT, _("Drop down")),
    (SELECT_MULTIPLE, _("Multi select")),
    (RADIO_MULTIPLE, _("Radio buttons")),
    (FILE, _("File upload")),
    (DATE, _("Date")),
    (DATE_TIME, _("Date/time")),
    (DOB, _("Date of birth")),
    (HIDDEN, _("Hidden")),
]

# Field classes for all available field types.
CLASSES = {
    TEXT: forms.CharField,
    TEXTAREA: forms.CharField,
    EMAIL: forms.EmailField,
    CHECKBOX: forms.BooleanField,
    CHECKBOX_MULTIPLE: forms.MultipleChoiceField,
    SELECT: forms.ChoiceField,
    SELECT_MULTIPLE: forms.MultipleChoiceField,
    RADIO_MULTIPLE: forms.ChoiceField,
    FILE: forms.FileField,
    DATE: forms.DateField,
    DATE_TIME: forms.DateTimeField,
    DOB: forms.DateField,
    HIDDEN: forms.CharField,
    NUMBER: forms.FloatField,
    URL: forms.URLField,
}

# Widgets for field types where a specialised widget is required.
WIDGETS = {
    TEXTAREA: forms.Textarea,
    CHECKBOX_MULTIPLE: forms.CheckboxSelectMultiple,
    RADIO_MULTIPLE: forms.RadioSelect,
    DATE: SelectDateWidget,
    DOB: SelectDateWidget,
    HIDDEN: forms.HiddenInput,
}

# Some helper groupings of field types.
CHOICES = (CHECKBOX, SELECT, RADIO_MULTIPLE)
DATES = (DATE, DATE_TIME, DOB)
MULTIPLE = (CHECKBOX_MULTIPLE, SELECT_MULTIPLE)

# HTML5 Widgets
if USE_HTML5:
    WIDGETS.update({
        DATE: html5_field("date", forms.DateInput),
        DATE_TIME: html5_field("datetime", forms.DateTimeInput),
        DOB: html5_field("date", forms.DateInput),
        EMAIL: html5_field("email", forms.TextInput),
        NUMBER: html5_field("number", forms.TextInput),
        URL: html5_field("url", forms.TextInput),
    })

META_REQUIRED_KEYS = {}
META_OPTIONAL_KEYS = {}
CHOICES_REQUIRED_KEYS = {}
CHOICES_OPTIONAL_KEYS = {}


for field_id, field_name in NAMES:
    META_REQUIRED_KEYS[field_id] = []
    META_OPTIONAL_KEYS[field_id] = []
    CHOICES_REQUIRED_KEYS[field_id] = ["text", "score", "slug"]
    CHOICES_OPTIONAL_KEYS[field_id] = []


def add_fields(fields_properties, strategy, meta_required_keys,
               meta_optional_keys, choices_required_keys,
               choices_optional_keys):
    """
    The `fields` parameter expects a list of tuples, each containing
    the following values: (field name, field path, widget path)
    For instance: [("Horizontal slider", "forms.IntegerField", "custom_widgets.HorizontalSlider"),
                   ("Icon choice", "forms.ChoiceField", "custom_widgets.IconChoice")]
    """
    global NAMES, META_REQUIRED_KEYS, META_OPTIONAL_KEYS, CHOICES_REQUIRED_KEYS, CHOICES_OPTIONAL_KEYS
    for prop in fields_properties:
        field_id = prop['field_id']
        try:
            if field_id in CLASSES:
                # This should never happen
                err = "ID %s for field %s in FORMS_EXTRA_FIELDS already exists"
                raise ImproperlyConfigured(err % (field_id, prop['name']))
            if prop['type']:
                CLASSES[field_id] = import_attr(prop['type'])
            else:
                CLASSES[field_id] = None
            NAMES += ((field_id, _(prop['name'])),)
            META_REQUIRED_KEYS[field_id] = prop.get('meta_required_keys', []) + meta_required_keys
            META_OPTIONAL_KEYS[field_id] = prop.get('meta_optional_keys', []) + meta_optional_keys
            CHOICES_REQUIRED_KEYS[field_id] = prop.get('choices_required_keys', []) + choices_required_keys + ['text']
            CHOICES_OPTIONAL_KEYS[field_id] = prop.get('choices_optional_keys', []) + choices_optional_keys
            if strategy == "backend":
                WIDGETS[field_id] = import_attr(prop['widget'])
            elif strategy == "frontend":
                WIDGETS[field_id] = prop['widget']
            else:
                raise ImproperlyConfigured("The 'strategy' field in the forms_builder fields configuration "
                                           "must be either 'backend' or 'frontend'")
        except KeyError, e:
            raise ImproperlyConfigured(
                "Each custom field definition must have a '%s' key" % e.message)

for template_name, template_properties in EXTRA_FIELDS.items():
    try:
        add_fields(template_properties["fields"], template_properties["strategy"],
                   template_properties.get("meta_required_keys", []),
                   template_properties.get("meta_optional_keys", []),
                   template_properties.get("choices_required_keys", []),
                   template_properties.get("choices_optional_keys", []))
    except KeyError:
        raise ImproperlyConfigured("Each template definition in settings.FORMS_BUILDER_EXTRA_FIELDS"
                                   "must have a 'fields' keys which is the list of widgets made"
                                   "available by the template")
