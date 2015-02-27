from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured
from django import forms
from django.forms.extras import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from forms_builder.forms.settings import USE_HTML5, EXTRA_FIELDS
from forms_builder.forms.utils import html5_field, import_attr
from django.conf import settings


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

def add_fields(fields):
    """
    The `fields` parameter expects a list of tuples, each containing the following values:
    (field name, field path, widget path)
    For instance: [("Horizontal slider", "forms.IntegerField", "custom_widgets.HorizontalSlider"),
                   ("Icon choice", "forms.ChoiceField", "custom_widgets.IconChoice"]
    """
    global NAMES
    # Get the first unused ID
    field_id = max([name[0] for name in NAMES]) + 1
    for field_name, field_path, widget_path in fields:
        if field_id in CLASSES:
            # This should never happen
            err = "ID %s for field %s in FORMS_EXTRA_FIELDS already exists"
            raise ImproperlyConfigured(err % (field_id, field_name))
        CLASSES[field_id] = import_attr(field_path)
        NAMES += ((field_id, _(field_name)),)
    	WIDGETS[field_id] = import_attr(widget_path)
        field_id += 1

for template_name, fields in EXTRA_FIELDS.items():
    add_fields(fields)
