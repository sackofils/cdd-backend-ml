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
from authentication.models import OrganismType
from dashboard.organism_type.forms import OrganismTypeForm, UpdateOrganismTypeForm
from django.forms.models import inlineformset_factory
from django.contrib import messages

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin
)


class OrganismTypeListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = OrganismType
    queryset = OrganismType.objects.all()
    template_name = 'organism_type/list.html'
    context_object_name = 'entries'
    active_level1 = "organism_type"
    title = gettext_lazy('Organism Type')
    breadcrumb = [{
        'url': '',
        'title': title
    }]

    def get_queryset(self):
        return super().get_queryset()


class OrganismTypeDetailView(LoginRequiredMixin, generic.DetailView):
    active_level1 = "organism_type"
    template_name = 'organism_type/detail.html'
    queryset = OrganismType.objects.all()


class OrganismTypeListTableView(LoginRequiredMixin, generic.ListView):
    template_name = 'organism_type/organism_list.html'
    context_object_name = 'entries'

    def get_results(self):
        return list(OrganismType.objects.all())

    def get_queryset(self):
        return self.get_results()


class OrganismTypeInline():
    form_class = OrganismTypeForm
    model = OrganismType
    template_name = 'organism_type/create_update.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect("dashboard:organism_type:list")


class CreateOrganismTypeView(OrganismTypeInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin,
                             generic.FormView):
    template_name = 'organism_type/create_update.html'
    title = gettext_lazy("Create Organism Type")
    active_level1 = "organism_type"
    form_class = OrganismTypeForm
    success_url = reverse_lazy('dashboard:organism_type:list')
    breadcrumb = [{
        'url': reverse_lazy('dashboard:organism_type:list'),
        'title': gettext_lazy('Organism Types')
    },
        {
            'url': '',
            'title': title
        }]


class UpdateOrganismTypeView(OrganismTypeInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin,
                             generic.UpdateView):
    model = OrganismType
    template_name = 'organism_type/create_update.html'
    title = gettext_lazy('Edit Organism type')
    active_level1 = 'organism_type'
    form_class = UpdateOrganismTypeForm
    breadcrumb = [{
        'url': reverse_lazy('dashboard:organism_type:list'),
        'title': gettext_lazy('Organism Type')
    },
        {
            'url': '',
            'title': title
        }]
