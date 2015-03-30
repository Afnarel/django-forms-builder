# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from email_extras.utils import send_mail_template

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form
from forms_builder.forms.settings import EMAIL_FAIL_SILENTLY
from forms_builder.forms.signals import form_invalid, form_valid
from forms_builder.forms.utils import split_choices, get_form_conf_for
from fields import WIDGETS
from json import dumps, loads


def create_json(form, conf):
    json = []
    for field in form.fields.all():
        data = {}
        try:
            data.update(loads(field.meta))
        except ValueError:
            pass
        data['type'] = WIDGETS[field.field_type]
        data['titleText'] = field.label
        data['isAvoidable'] = (not field.required)
        data['name'] = field.slug
        try:
            data['choices'] = loads(field.choices)
            for choice in data['choices']:
                choice['value'] = choice['text']
        except ValueError:
            pass
        json.append(data)
    return json


class FormDetail(TemplateView):

    # template_name = "forms/form_detail.html"

    def __init__(self, **kwargs):
        super(FormDetail, self).__init__(**kwargs)
        # self.published = Form.objects.published(for_user=self.request.user)
        # print self.published

    def get_form(self, slug):
        published = Form.objects.published(for_user=self.request.user)
        return get_object_or_404(published, slug=slug)

    def get_template_names(self):
        if self.form.template:
            return ["forms/%s/form_detail.html" % self.form.template]
        return "forms/form_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FormDetail, self).get_context_data(**kwargs)
        self.form = self.get_form(kwargs["slug"])
        self.conf = get_form_conf_for(self.form.template)
        # If forms are generated using HTML widgets they need the form
        if self.conf['strategy'] == "backend":
            context["form"] = self.form
        # If forms are generated in Javascript, they need the JSON to create them
        elif self.conf['strategy'] == "frontend":
            context["form"] = mark_safe(dumps(create_json(self.form, self.conf), ensure_ascii=False, indent=4))
        else:
            raise ImproperlyConfigured("The 'strategy' key in forms configuration must "
                                       "be either 'backend' or 'frontend'")
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        login_required = self.form.login_required
        if login_required and not request.user.is_authenticated():
            path = urlquote(request.get_full_path())
            bits = (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
            return redirect("%s?%s=%s" % bits)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form_for_form = FormForForm(self.form, RequestContext(request),
                                    request.POST or None,
                                    request.FILES or None)
        if not form_for_form.is_valid():
            form_invalid.send(sender=request, form=form_for_form)
        else:
            # Attachments read must occur before model save,
            # or seek() will fail on large uploads.
            attachments = []
            for f in form_for_form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))
            entry = form_for_form.save()
            form_valid.send(sender=request, form=form_for_form, entry=entry)
            self.send_emails(request, form_for_form, self.form, entry, attachments)
            if not self.request.is_ajax():
                return redirect(self.form.redirect_url or
                    reverse("form_sent", kwargs={"slug": self.form.slug}))
        context.update({"form_for_form": form_for_form})
        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax() and self.conf['strategy'] == 'backend':
            json_context = json.dumps({
                "errors": context["form_for_form"].errors,
                "form": context["form_for_form"].as_p(),
                "message": context["form"].response,
            })
            return HttpResponse(json_context, content_type="application/json")
        return super(FormDetail, self).render_to_response(context, **kwargs)

    def send_emails(self, request, form_for_form, form, entry, attachments):
        subject = form.email_subject
        if not subject:
            subject = "%s - %s" % (form.title, entry.entry_time)
        fields = []
        for (k, v) in form_for_form.fields.items():
            value = form_for_form.cleaned_data[k]
            if isinstance(value, list):
                value = ", ".join([i.strip() for i in value])
            fields.append((v.label, value))
        context = {
            "fields": fields,
            "message": form.email_message,
            "request": request,
        }
        email_from = form.email_from or settings.DEFAULT_FROM_EMAIL
        email_to = form_for_form.email_to()
        if email_to and form.send_email:
            send_mail_template(subject, "form_response", email_from,
                               email_to, context=context,
                               fail_silently=EMAIL_FAIL_SILENTLY)
        headers = None
        if email_to:
            headers = {"Reply-To": email_to}
        email_copies = split_choices(form.email_copies)
        if email_copies:
            send_mail_template(subject, "form_response_copies", email_from,
                               email_copies, context=context,
                               attachments=attachments,
                               fail_silently=EMAIL_FAIL_SILENTLY,
                               headers=headers)

form_detail = login_required(FormDetail.as_view())


@login_required
def form_sent(request, slug, template="forms/form_sent.html"):
    """
    Show the response message.
    """
    published = Form.objects.published(for_user=request.user)
    context = {"form": get_object_or_404(published, slug=slug)}
    return render_to_response(template, context, RequestContext(request))
