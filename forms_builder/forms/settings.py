from __future__ import unicode_literals

from django.conf import settings


# The maximum allowed length for field values.
FIELD_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_FIELD_MAX_LENGTH", 2000)

# The maximum allowed length for field labels.
LABEL_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_LABEL_MAX_LENGTH", 200)

# Sequence of custom fields that will be added to the form field types.
EXTRA_FIELDS = getattr(settings, "FORMS_BUILDER_EXTRA_FIELDS", ())

# The absolute path where files will be uploaded to.
UPLOAD_ROOT = getattr(settings, "FORMS_BUILDER_UPLOAD_ROOT", None)

# Boolean controlling whether HTML5 form fields are used.
USE_HTML5 = getattr(settings, "FORMS_BUILDER_USE_HTML5", True)

# Boolean controlling whether forms are associated to Django's Sites framework.
USE_SITES = getattr(settings, "FORMS_BUILDER_USE_SITES",
                    "django.contrib.sites" in settings.INSTALLED_APPS)

# Boolean controlling whether form slugs are editable in the admin.
EDITABLE_SLUGS = getattr(settings, "FORMS_BUILDER_EDITABLE_SLUGS", False)

# Char to use as a field delimiter when exporting form responses as CSV.
CSV_DELIMITER = getattr(settings, "FORMS_BUILDER_CSV_DELIMITER", ",")

# The maximum allowed length for field help text
HELPTEXT_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_HELPTEXT_MAX_LENGTH", 100)

# The maximum allowed length for field choices
CHOICES_MAX_LENGTH = getattr(settings, "FORMS_BUILDER_CHOICES_MAX_LENGTH", 1000)

# Does sending emails fail silently or raise an exception.
EMAIL_FAIL_SILENTLY = getattr(settings, "FORMS_BUILDER_EMAIL_FAIL_SILENTLY",
                              settings.DEBUG)

# Path to the folder that will contain the rules executed each time a form is submitted
RULES_PATH = getattr(settings, "FORMS_BUILDER_RULES_PATH", None)

# Django SITE_ID - need a default since no longer provided in settings.py.
SITE_ID = getattr(settings, "SITE_ID", 1)
