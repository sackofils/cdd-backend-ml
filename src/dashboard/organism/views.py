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
from authentication.models import OrganismType, Organism
from dashboard.organism.forms import OrganismForm, UpdateOrganismForm
from django.forms.models import inlineformset_factory
from django.contrib import messages

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin
)


class OrganismListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Organism
    queryset = Organism.objects.all()
    template_name = 'organism/list.html'
    context_object_name = 'entries'
    active_level1 = "organisms"
    title = gettext_lazy('Organism')
    breadcrumb = [{
        'url': '',
        'title': title
    }]

    def get_queryset(self):
        return super().get_queryset()


class OrganismDetailView(LoginRequiredMixin, generic.DetailView):
    active_level1 = "organisms"
    template_name = 'organism/detail.html'
    queryset = Organism.objects.all()


class OrganismListTableView(LoginRequiredMixin, generic.ListView):
    template_name = 'organism/organism_list.html'
    context_object_name = 'entries'

    def get_results(self):
        return list(Organism.objects.all())

    def get_queryset(self):
        return self.get_results()


class OrganismInline():
    form_class = OrganismForm
    model = Organism
    template_name = 'organism/create_update.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect("dashboard:organisms:list")


class CreateOrganismView(OrganismInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin,
                             generic.FormView):
    template_name = 'organism/create_update.html'
    title = gettext_lazy("Create Organism")
    active_level1 = "organisms"
    form_class = OrganismForm
    success_url = reverse_lazy('dashboard:organisms:list')
    breadcrumb = [{
        'url': reverse_lazy('dashboard:organisms:list'),
        'title': gettext_lazy('Organisms')
    },
        {
            'url': '',
            'title': title
        }]


class UpdateOrganismView(OrganismInline, PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin,
                             generic.UpdateView):
    model = Organism
    template_name = 'organism/create_update.html'
    title = gettext_lazy('Edit Organism')
    active_level1 = 'organisms'
    form_class = UpdateOrganismForm
    breadcrumb = [{
        'url': reverse_lazy('dashboard:organisms:list'),
        'title': gettext_lazy('Organism')
    },
        {
            'url': '',
            'title': title
        }]
