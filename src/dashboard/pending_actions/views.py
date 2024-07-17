from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy
from django.shortcuts import redirect, get_list_or_404
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient
from django.contrib import messages
from authentication.models import Facilitator, Organism

from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin
)


class PendingActionsMixin:
    projects = None
    facilitators = None
    query_result = []

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        self.projects = nsc.get_db("process_design").get_query_result({"type": "project"})
        self.facilitators = Facilitator.objects.filter()
        self.query_result = []
        try:
            for facilitator in self.facilitators:
                facilitator_db = nsc.get_db(facilitator.no_sql_db_name)
                facilitator_doc = facilitator_db.get_query_result(
                    {
                        "type": "facilitator"
                    }
                )[0]
                tasks = facilitator_db.get_query_result(
                    {
                        "type": "task",
                        "completed": True,
                        "validated": False
                    }
                )
                self.query_result.append({
                    "facilitator": facilitator_doc,
                    "tasks": tasks
                })
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_project_by_id(self, id):
        found = None
        for project in self.projects:
            if project.get('_id') == id:
                found = project
                break
        return found


class PendingActionsListView(PageMixin, LoginRequiredMixin, generic.ListView):
    template_name = "pending_actions/list.html"
    context_object_name = "pending_actions"
    active_level1 = "pending_actions"
    title = gettext_lazy("Pending actions")
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return []


class PendingActionsTableListView(PendingActionsMixin, LoginRequiredMixin, generic.ListView):
    template_name = "pending_actions/pending_action_list.html"
    context_object_name = "pending_actions"

    task_fields = ["_id", "_rev", "type", "project_id", "phase_id", "phase_name", "activity_id", "activity_name",
                   "name", "order", "description", "completed", "completed_date", "administrative_level_id",
                   "administrative_level_name"]

    task_selector = {"$or": [{"completed": True}, {"action_complete_by.type": "complete"}]}

    def get_results(self):
        # for f in Facilitator.objects.filter(develop_mode=False, training_mode=False):
        connected_user = self.request.user
        results = []
        query = Q()
        nsc = NoSQLClient()
        if not connected_user.is_superuser:
            query |= Q(supervisor=connected_user)
            query |= Q(coordinator=connected_user)

        for f in Facilitator.objects.filter(query):
            already_count_facilitator = False
            facilitator_db = nsc.get_db(f.no_sql_db_name)
            query_result = facilitator_db.get_query_result({"type": "facilitator"})[:]
            if query_result:
                facilitator = query_result[0]
                tasks = facilitator_db.get_query_result(self.task_selector)[:]
                if tasks:
                    results.append({
                        'facilitator': facilitator,
                        'tasks': tasks
                    })
        return results

    def get_queryset(self):
        return []

    def get_facilitator_info(self, facilitator):
        res = None
        for instance in self.facilitators:
            if instance.username == facilitator.get('email'):
                res = instance
                break
        return res

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.get_results()

        res = []
        if object_list:
            for _ in object_list:
                facilitator = _.get('facilitator')
                for task in _.get('tasks'):
                    project = self.get_project_by_id(task.get("project_id"))
                    item = {
                        "project": project,
                        "facilitator": facilitator,
                        "facilitator_db_name": self.get_facilitator_info(facilitator).no_sql_db_name,
                        "village": task.get('administrative_level_name'),
                        "task": task,
                        "status": task.get('completed')
                    }
                    res.append(item)

        context["pending_actions"] = res
        return context
