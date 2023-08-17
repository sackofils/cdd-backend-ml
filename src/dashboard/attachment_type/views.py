from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy
from django.shortcuts import redirect, get_list_or_404
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient
from process_manager.models import AttachmentType
from dashboard.attachment_type.forms import AttachmentTypeForm, UpdateAttachmentTypeForm
from django.forms.models import inlineformset_factory
from django.contrib import messages

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin, SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin
)


class AttachmentTypeListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = AttachmentType
    queryset = AttachmentType.objects.all()
    template_name = 'attachment_type/list.html'
    context_object_name = 'attachments'
    active_level1 = "attachments"
    title = gettext_lazy('Attachments')
    breadcrumb = [{
        'url': '',
        'title': title
    }]

    def get_queryset(self):
        return super().get_queryset()


class AttachmentTypeDetailView(LoginRequiredMixin, generic.DetailView):
    active_level1 = "attachments"
    template_name = 'attachment_type/detail.html'
    queryset = AttachmentType.objects.all()


class AttachmentTypeListTableView(LoginRequiredMixin, generic.ListView):
    template_name = 'attachment_type/attachment_list.html'
    context_object_name = 'attachments'

    def get_results(self):
        return list(AttachmentType.objects.all())

    def get_queryset(self):
        return self.get_results()


class AttachmentTypeInline():
    form_class = AttachmentTypeForm
    model = AttachmentType
    template_name = 'attachment_type/create_update.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect("dashboard:attachment_type:list")

class CreateAttachmentTypeView(AttachmentTypeInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView):
    template_name = 'attachment_type/create_update.html'
    title = gettext_lazy("Create Attachment")
    active_level1 = "attachments"
    form_class = AttachmentTypeForm
    success_url = reverse_lazy('dashboard:attachment_type:list')
    breadcrumb = [{
        'url': reverse_lazy('dashboard:attachment_type:list'),
        'title': gettext_lazy('Attachments')
    },
        {
            'url': '',
            'title': title
        }]


class UpdateAttachmentTypeView(AttachmentTypeInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin,
                         generic.UpdateView):
    model = AttachmentType
    template_name = 'attachment_type/create_update.html'
    title = gettext_lazy('Edit Attachment')
    active_level1 = 'attachments'
    form_class = UpdateAttachmentTypeForm
    breadcrumb = [{
        'url': reverse_lazy('dashboard:attachment_type:list'),
        'title': gettext_lazy('Attachments')
    },
        {
            'url': '',
            'title': title
        }]
