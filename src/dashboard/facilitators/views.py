from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy
from django.views import generic
from datetime import datetime

from process_manager.models import Phase, Activity
from authentication.models import Facilitator
from dashboard.facilitators.forms import (
    FacilitatorForm,
    FilterTaskForm,
    UpdateFacilitatorForm,
    FilterFacilitatorForm,
)
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from no_sql_client import NoSQLClient
from dashboard.utils import (
    get_all_docs_administrative_levels_by_type_and_administrative_id,
    get_all_docs_administrative_levels_by_type_and_parent_id,
)
from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin,
    SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin,
)


class FacilitatorListView(PageMixin, LoginRequiredMixin, generic.ListView):
    model = Facilitator
    queryset = Facilitator.objects.all()
    template_name = "facilitators/list.html"
    context_object_name = "facilitators"
    title = gettext_lazy("Facilitators")
    active_level1 = "facilitators"
    breadcrumb = [
        {"url": "", "title": title},
    ]

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FilterFacilitatorForm()

        context["is_training"] = bool(self.request.GET.get("training", "0") != "0")
        context["is_develop"] = bool(self.request.GET.get("develop", "0") != "0")

        return context


class FacilitatorMixin:
    doc = None
    obj = None
    facilitator_db = None
    facilitator_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.facilitator_db_name = kwargs["id"]
            self.facilitator_db = nsc.get_db(self.facilitator_db_name)
            query_result = self.facilitator_db.get_query_result(
                {"type": "facilitator"}
            )[:]
            self.doc = self.facilitator_db[query_result[0]["_id"]]
            self.obj = get_object_or_404(Facilitator, no_sql_db_name=kwargs["id"])
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class FacilitatorListTableView(LoginRequiredMixin, generic.ListView):
    template_name = "facilitators/facilitator_list.html"
    context_object_name = "facilitators"

    def get_results(self):
        id_region = self.request.GET.get("id_region")
        id_cercle = self.request.GET.get("id_cercle")
        id_commune = self.request.GET.get("id_commune")
        id_village = self.request.GET.get("id_village")
        type_field = self.request.GET.get("type_field")
        facilitators = []
        if (
            id_region or id_cercle or id_commune or id_village
        ) and type_field:
            _type = None
            if id_region and type_field == "region":
                _type = "region"
            elif id_cercle and type_field == "commune":
                _type = "cercle"
            elif id_commune and type_field == "cercle":
                _type = "commune"
            elif id_village and type_field == "village":
                _type = "village"

            nsc = NoSQLClient()

            liste_cercles = []
            liste_communes = []
            liste_villages = []
            administrative_levels = nsc.get_db("administrative_levels").all_docs(
                include_docs=True
            )["rows"]

            if _type == "region":
                region = (
                    get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type.title(), id_region
                    )
                )
                region = region[:][0]
                _type = "cercle"
                liste_cercles = (
                    get_all_docs_administrative_levels_by_type_and_parent_id(
                        administrative_levels,
                        _type.title(),
                        region["administrative_id"],
                    )[:]
                )

            if _type == "cercle":
                if not liste_cercles:
                    liste_cercles = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type.title(), id_cercle
                    )[
                        :
                    ]
                _type = "commune"
                for commune in liste_communes:
                    [
                        liste_communes.append(elt)
                        for elt in get_all_docs_administrative_levels_by_type_and_parent_id(
                            administrative_levels,
                            _type.title(),
                            commune["administrative_id"],
                        )[
                            :
                        ]
                    ]

            if _type == "commune":
                if not liste_communes:
                    liste_communes = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type.title(), id_commune
                    )[
                        :
                    ]
                _type = "village"
                for commune in liste_communes:
                    [
                        liste_villages.append(elt)
                        for elt in get_all_docs_administrative_levels_by_type_and_parent_id(
                            administrative_levels,
                            _type.title(),
                            commune["administrative_id"],
                        )[
                            :
                        ]
                    ]

            if _type == "village":
                if not liste_villages:
                    liste_villages = get_all_docs_administrative_levels_by_type_and_administrative_id(
                        administrative_levels, _type.title(), id_village
                    )[
                        :
                    ]

            for f in Facilitator.objects.filter(
                develop_mode=False, training_mode=False
            ):
                already_count_facilitator = False
                facilitator_db = nsc.get_db(f.no_sql_db_name)
                query_result = facilitator_db.get_query_result({"type": "facilitator"})[
                    :
                ]
                if query_result:
                    doc = query_result[0]
                    for _village in doc["administrative_levels"]:
                        if str(
                            _village["id"]
                        ).isdigit():  # Verify if id contain only digit
                            for village in liste_villages:
                                if str(_village["id"]) == str(
                                    village["administrative_id"]
                                ):
                                    if not already_count_facilitator:
                                        facilitators.append(f)
                                        already_count_facilitator = True
        else:
            # facilitators = list(Facilitator.objects.all())
            is_training = bool(self.request.GET.get("is_training", "False") == "True")
            is_develop = bool(self.request.GET.get("is_develop", "False") == "True")
            facilitators = Facilitator.objects.filter(
                develop_mode=is_develop, training_mode=is_training
            )
        return facilitators

    def get_queryset(self):
        return self.get_results()

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context


class FacilitatorsPercentListView(
    FacilitatorMixin, AJAXRequestMixin, LoginRequiredMixin, generic.ListView
):
    template_name = "facilitators/facilitator_percent_completed.html"
    context_object_name = "facilitator_percent_completed"

    def get_results(self):
        return self.facilitator_db.get_query_result({"type": "task"})

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_tasks_completed = 0
        total_tasks_uncompleted = 0
        total_tasks = 0

        object_list = self.get_results()

        if object_list:
            for _ in object_list:
                if _.get("completed"):
                    total_tasks_completed += 1
                else:
                    total_tasks_uncompleted += 1
                total_tasks += 1

        context["percentage_tasks_completed"] = (
            ((total_tasks_completed / total_tasks) * 100) if total_tasks else 0
        )

        return context


class FacilitatorsPercentView(
    AJAXRequestMixin, LoginRequiredMixin, JSONResponseMixin, generic.View
):
    def post(self, request, *args, **kwargs):
        liste = request.POST.getlist("liste[]")
        d = {}

        nsc = NoSQLClient()
        for f in liste:
            facilitator_db = nsc.get_db(f)
            docs = facilitator_db.get_query_result({"type": "task"})

            total_tasks_completed = 0
            total_tasks_uncompleted = 0
            total_tasks = 0
            if docs:
                for _ in docs:
                    if _.get("completed"):
                        total_tasks_completed += 1
                    else:
                        total_tasks_uncompleted += 1
                    total_tasks += 1

            d[f] = ((total_tasks_completed / total_tasks) * 100) if total_tasks else 0

        return self.render_to_json_response(d, safe=False)


class FacilitatorDetailView(
    FacilitatorMixin, PageMixin, LoginRequiredMixin, generic.DetailView
):
    template_name = "facilitators/profile.html"
    context_object_name = "facilitator_doc"
    title = gettext_lazy("Facilitator Profile")
    active_level1 = "facilitators"
    model = Facilitator
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:facilitators:list"),
            "title": gettext_lazy("Facilitators"),
        },
        {"url": "", "title": title},
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["facilitator"] = self.obj
        context["form"] = FilterTaskForm(
            initial={"facilitator_db_name": self.facilitator_db_name}
        )

        facilitator_docs = self.facilitator_db.all_docs(include_docs=True)["rows"]
        last_activity_date = "0000-00-00 00:00:00"
        for doc in facilitator_docs:
            doc = doc.get("doc")
            if (
                doc.get("type") == "task"
                and doc.get("last_updated")
                and last_activity_date < doc.get("last_updated")
            ):
                last_activity_date = doc.get("last_updated")

        if last_activity_date == "0000-00-00 00:00:00":
            context["facilitator_doc"]["last_activity_date"] = None
        else:
            context["facilitator_doc"]["last_activity_date"] = datetime.strptime(
                last_activity_date, "%Y-%m-%d %H:%M:%S"
            )

        # facilitator_docs = self.facilitator_db.all_docs(include_docs=True)['rows']

        # dict_administrative_levels_with_infos = {}
        # tasks = []
        # administrative_levels = []
        # for doc in facilitator_docs:
        #     doc = doc.get('doc')
        #     if doc.get('type') == "facilitator":
        #         administrative_levels = doc.get('administrative_levels')
        #         break

        # total_tasks_completed = 0
        # total_tasks_uncompleted = 0
        # total_tasks = 0
        # for doc in facilitator_docs:
        #     doc = doc.get('doc')
        #     if doc.get('type') == "task":
        #         tasks.append(doc)
        #         if doc.get("completed"):
        #             total_tasks_completed += 1
        #         else:
        #             total_tasks_uncompleted += 1
        #         total_tasks += 1

        #         for administrative_level in administrative_levels:
        #             if str(administrative_level.get("id")) == str(doc.get("administrative_level_id")):
        #                 if dict_administrative_levels_with_infos.get(administrative_level.get("name")):
        #                     if doc.get("completed"):
        #                         dict_administrative_levels_with_infos[administrative_level.get("name")]['total_tasks_completed'] += 1
        #                     else:
        #                         dict_administrative_levels_with_infos[administrative_level.get("name")]['total_tasks_uncompleted'] += 1
        #                     dict_administrative_levels_with_infos[administrative_level.get("name")]['total_tasks'] += 1
        #                 else:
        #                     if doc.get("completed"):
        #                         dict_administrative_levels_with_infos[administrative_level.get("name")] = {
        #                             'total_tasks_completed': 1,
        #                             'total_tasks_uncompleted': 0
        #                         }
        #                     else:
        #                         dict_administrative_levels_with_infos[administrative_level.get("name")] = {
        #                             'total_tasks_completed': 0,
        #                             'total_tasks_uncompleted': 1
        #                         }
        #                     dict_administrative_levels_with_infos[administrative_level.get("name")]['total_tasks'] = 1

        # context['total_tasks_completed'] = total_tasks_completed
        # context['total_tasks_uncompleted'] = total_tasks_uncompleted
        # context['total_tasks'] = total_tasks
        # context['percentage_tasks_completed'] = ((total_tasks_completed/total_tasks)*100) if total_tasks else 0

        # for key, value in dict_administrative_levels_with_infos.items():
        #     dict_administrative_levels_with_infos[key]["percentage_tasks_completed"] = ((value["total_tasks_completed"]/value["total_tasks"])*100) if value["total_tasks"] else 0
        #     del dict_administrative_levels_with_infos[key]["total_tasks"]
        # context['dict_administrative_levels_with_infos'] = dict_administrative_levels_with_infos

        return context

    def get_object(self, queryset=None):
        return self.doc


class FacilitatorTaskListView(
    FacilitatorMixin, AJAXRequestMixin, LoginRequiredMixin, generic.ListView
):
    template_name = "facilitators/task_list.html"
    context_object_name = "tasks"

    def get_results(self):
        administrative_level_id = self.request.GET.get("administrative_level")
        # phase_id = self.request.GET.get('phase')
        # activity_id = self.request.GET.get('activity')
        phase_name = self.request.GET.get("phase")
        activity_name = self.request.GET.get("activity")
        task_name = self.request.GET.get("task")

        selector = {"type": "task"}

        if administrative_level_id:
            selector["administrative_level_id"] = administrative_level_id
        if phase_name:
            selector["phase_name"] = phase_name
        if activity_name:
            selector["activity_name"] = activity_name
        if task_name:
            selector["name"] = task_name

        return self.facilitator_db.get_query_result(selector)

    def get_queryset(self):
        index = int(self.request.GET.get("index"))
        offset = int(self.request.GET.get("offset"))
        phases = Phase.objects.all()
        activities = Activity.objects.all()
        _list = []
        object_list = self.get_results()
        if object_list:
            for _ in object_list:
                _["phase_order"] = 0
                _["activity_order"] = 0
                for phase_obj in phases:
                    if phase_obj.name == _["phase_name"]:
                        _["phase_order"] = phase_obj.order
                        break
                for activity_obj in activities:
                    if activity_obj.name == _["activity_name"]:
                        _["activity_order"] = activity_obj.order
                        break
                _list.append(_)

        return sorted(
            _list,
            key=lambda obj: (
                str(obj["phase_order"]) + str(obj["activity_order"]) + str(obj["order"])
            ),
        )[index : index + offset]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_tasks_completed = 0
        total_tasks_uncompleted = 0
        total_tasks = 0
        dict_administrative_levels_with_infos = {}

        object_list = self.get_results()
        administrative_levels = self.facilitator_db.get_query_result(
            {"type": "facilitator"}
        )[:][0]["administrative_levels"]

        if object_list:
            for _ in object_list:
                if _.get("completed"):
                    total_tasks_completed += 1
                else:
                    total_tasks_uncompleted += 1
                total_tasks += 1

                for administrative_level in administrative_levels:
                    if str(administrative_level.get("id")) == str(
                        _.get("administrative_level_id")
                    ):
                        if dict_administrative_levels_with_infos.get(
                            administrative_level.get("name")
                        ):
                            if _.get("completed"):
                                dict_administrative_levels_with_infos[
                                    administrative_level.get("name")
                                ]["total_tasks_completed"] += 1
                            else:
                                dict_administrative_levels_with_infos[
                                    administrative_level.get("name")
                                ]["total_tasks_uncompleted"] += 1
                            dict_administrative_levels_with_infos[
                                administrative_level.get("name")
                            ]["total_tasks"] += 1
                        else:
                            if _.get("completed"):
                                dict_administrative_levels_with_infos[
                                    administrative_level.get("name")
                                ] = {
                                    "total_tasks_completed": 1,
                                    "total_tasks_uncompleted": 0,
                                }
                            else:
                                dict_administrative_levels_with_infos[
                                    administrative_level.get("name")
                                ] = {
                                    "total_tasks_completed": 0,
                                    "total_tasks_uncompleted": 1,
                                }
                            dict_administrative_levels_with_infos[
                                administrative_level.get("name")
                            ]["total_tasks"] = 1

        context["total_tasks_completed"] = total_tasks_completed
        context["total_tasks_uncompleted"] = total_tasks_uncompleted
        context["total_tasks"] = total_tasks
        context["percentage_tasks_completed"] = (
            ((total_tasks_completed / total_tasks) * 100) if total_tasks else 0
        )

        for key, value in dict_administrative_levels_with_infos.items():
            dict_administrative_levels_with_infos[key]["percentage_tasks_completed"] = (
                ((value["total_tasks_completed"] / value["total_tasks"]) * 100)
                if value["total_tasks"]
                else 0
            )
            del dict_administrative_levels_with_infos[key]["total_tasks"]
        context[
            "dict_administrative_levels_with_infos"
        ] = dict_administrative_levels_with_infos

        return context


class CreateFacilitatorFormView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView
):
    template_name = "facilitators/create.html"
    title = gettext_lazy("Create Facilitator")
    active_level1 = "facilitators"
    form_class = FacilitatorForm
    success_url = reverse_lazy("dashboard:facilitators:list")
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:facilitators:list"),
            "title": gettext_lazy("Facilitators"),
        },
        {"url": "", "title": title},
    ]

    def form_valid(self, form):
        data = form.cleaned_data
        password = make_password(data["password1"], salt=None, hasher="default")
        facilitator = Facilitator(
            username=data["username"], password=password, active=True
        )
        facilitator.save(replicate_design=False)
        doc = {
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
            "sex": data["sex"],
            "administrative_levels": data["administrative_levels"],
            "type": "facilitator",
        }
        nsc = NoSQLClient()
        facilitator_database = nsc.get_db(facilitator.no_sql_db_name)
        nsc.create_document(facilitator_database, doc)
        return super().form_valid(form)


class UpdateFacilitatorView(
    PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.UpdateView
):
    model = Facilitator
    template_name = "facilitators/update.html"
    title = gettext_lazy("Edit Facilitator")
    active_level1 = "facilitators"
    form_class = UpdateFacilitatorForm
    # success_url = reverse_lazy('dashboard:facilitators:list')
    breadcrumb = [
        {
            "url": reverse_lazy("dashboard:facilitators:list"),
            "title": gettext_lazy("Facilitators"),
        },
        {"url": "", "title": title},
    ]

    facilitator_db = None
    facilitator = None
    doc = None
    facilitator_db_name = None

    def dispatch(self, request, *args, **kwargs):
        nsc = NoSQLClient()
        try:
            self.facilitator = self.get_object()
            self.facilitator_db_name = self.facilitator.no_sql_db_name
            self.facilitator_db = nsc.get_db(self.facilitator_db_name)
            query_result = self.facilitator_db.get_query_result(
                {"type": "facilitator"}
            )[:]
            self.doc = self.facilitator_db[query_result[0]["_id"]]
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateFacilitatorView, self).get_context_data(**kwargs)
        form = ctx.get("form")
        ctx.setdefault("facilitator_doc", self.doc)
        if self.doc:
            if form:
                for label, field in form.fields.items():
                    try:
                        form.fields[label].value = self.doc[label]
                    except Exception as exc:
                        pass

                ctx.setdefault("form", form)
            ctx.setdefault(
                "facilitator_administrative_levels", self.doc["administrative_levels"]
            )

        return ctx

    def post(self, request, *args, **kwargs):
        if not self.facilitator_db_name:
            raise Http404("We don't find the database name for the facilitators.")

        form = UpdateFacilitatorForm(request.POST, instance=self.facilitator)
        if form.is_valid():
            return self.form_valid(form)
        return self.get(request, *args, **kwargs)

    def form_valid(self, form):
        data = form.cleaned_data
        facilitator = form.save(commit=False)
        facilitator = facilitator.simple_save()

        _administrative_levels = []
        for elt in data["administrative_levels"]:
            exists = False
            for _elt in _administrative_levels:
                if _elt.get("id") == elt.get("id"):
                    exists = True
            if not exists:
                _administrative_levels.append(elt)

        doc = {
            "phone": data["phone"],
            "email": data["email"],
            "name": data["name"],
            "sex": data["sex"],
            "administrative_levels": _administrative_levels,
        }
        nsc = NoSQLClient()
        nsc.update_doc(self.facilitator_db, self.doc["_id"], doc)
        return redirect("dashboard:facilitators:list")
