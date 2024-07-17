from django.shortcuts import render, redirect
from .forms import SupportForm, UpdateSupportForm
from .serializers import SupportSerializer
from no_sql_client import NoSQLClient
from django.conf import settings
from django.views import generic, View
from django.utils.translation import gettext_lazy
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import AJAXRequestMixin, PageMixin, JSONResponseMixin
from authentication.permissions import (
    CDDSpecialistPermissionRequiredMixin, SuperAdminPermissionRequiredMixin,
    AdminPermissionRequiredMixin
)
from django.http import Http404, HttpResponse
import base64


class SupportListView(PageMixin, LoginRequiredMixin, generic.ListView):
    template_name = 'supports/list.html'
    context_object_name = 'supports'
    title = gettext_lazy('Support')
    active_level1 = 'supports'
    breadcrumb = [
        {
            'url': '',
            'title': title
        },
    ]

    def get_queryset(self):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')
        return [doc for doc in db]


class SupportsListTableView(LoginRequiredMixin, generic.ListView):
    template_name = 'supports/support_list.html'
    context_object_name = 'supports'

    def get_results(self):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')
        supports = []
        for doc in db:
            attachment = None
            filename = None
            content_type = None
            if '_attachments' in doc:
                for filename in doc['_attachments']:
                    attachment = doc.get_attachment(filename)
                    content_type = doc['_attachments'][filename]['content_type']

            support = {
                'id': doc.get('_id'),
                'name': doc.get('name'),
                'description': doc.get('description'),
                # 'file': attachment,
                'filename': filename,
                'content_type': content_type,
            }
            supports.append(support)
        return supports

    def get_queryset(self):
        return self.get_results()


class SupportFileDownloadView(View):
    def get(self, request, support_id, filename):
        nsc = NoSQLClient()

        try:
            db = nsc.get_db('supports')
            doc = db[support_id]

            attachment = None
            if '_attachments' in doc:
                for filename in doc['_attachments']:
                    attachment = doc.get_attachment(filename)

        except Exception as e:
            print(str(e))
            raise Http404("Support or file not found")

        response = HttpResponse(attachment, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class CreateSupportFormView(PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView):
    template_name = 'supports/create.html'
    title = gettext_lazy('Add support')
    active_level1 = 'supports'
    form_class = SupportForm
    success_url = reverse_lazy('dashboard:supports:list')
    breadcrumb = [
        {
            'url': reverse_lazy('dashboard:supports:list'),
            'title': gettext_lazy('Supports')
        },
        {
            'url': '',
            'title': title
        }
    ]

    def form_valid(self, form):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')
        file_data = form.cleaned_data['file']
        support = {
            'name': form.cleaned_data['name'],
            'description': form.cleaned_data['description']
        }
        doc = db.create_document(support)
        doc.put_attachment(file_data.name, file_data.content_type, file_data)

        return super().form_valid(form)


class UpdateSupportView(PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView):
    template_name = 'supports/update.html'
    title = gettext_lazy('Edit Support')
    active_level1 = 'supports'
    breadcrumb = [
        {
            'url': reverse_lazy('dashboard:supports:list'),
            'title': gettext_lazy('Supports')
        },
        {
            'url': '',
            'title': title
        }
    ]

    support_db = None
    doc = None

    def get(self, request, support_id):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')

        try:
            doc = db[support_id]
        except Exception:
            raise Http404("Support not found")

        support_data = {
            'name': doc.get('name'),
            'description': doc.get('description'),
        }

        attachment = None
        filename = None
        content_type = None
        if '_attachments' in doc:
            for filename in doc['_attachments']:
                attachment = doc.get_attachment(filename)
                content_type = doc['_attachments'][filename]['content_type']

        support = {
            'id': support_id,
            'name': doc.get('name'),
            'description': doc.get('description'),
            'file': base64.b64encode(attachment).decode('utf-8') if attachment else None,
            'filename': filename,
            'content_type': content_type
        }
        form = UpdateSupportForm(initial=support_data)
        return render(request, self.template_name, {'form': form, 'support_id': support_id, 'support': support})

    def post(self, request, support_id):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')

        try:
            doc = db[support_id]
        except Exception:
            raise Http404("Support not found")

        form = UpdateSupportForm(request.POST, request.FILES)
        if form.is_valid():
            doc['name'] = form.cleaned_data['name']
            doc['description'] = form.cleaned_data['description']
            doc.save()

            if 'file' in request.FILES:
                file = request.FILES['file']
                file_data = file.read()
                # Supprimer l'ancienne pièce jointe s'il y en a une
                if '_attachments' in doc:
                    doc.delete_attachment(list(doc['_attachments'].keys())[0])
                # Attacher le nouveau fichier
                doc.put_attachment(data=file_data, attachment=file.name, content_type=file.content_type)

            return redirect('dashboard:supports:list')
        return render(request, self.template_name, {'form': form, 'support_id': support_id})


def delete(request, id):
    nsc = NoSQLClient()
    nsc_database = nsc.get_db("supports")
    support = nsc_database[id]
    if request.method == 'POST':
        nsc.delete_document(nsc_database, id)
        return redirect('dashboard:supports:list')

    return render(request, 'supports/support_confirm_delete.html',
                  {'support': support})


class SupportDetailView(View):
    template_name = 'supports/support_detail.html'

    def get(self, request, support_id):
        nsc = NoSQLClient()
        db = nsc.get_db('supports')

        try:
            doc = db[support_id]
        except Exception:
            raise Http404("Support not found")

        attachment = None
        filename = None
        content_type = None
        if '_attachments' in doc:
            for filename in doc['_attachments']:
                attachment = doc.get_attachment(filename)
                content_type = doc['_attachments'][filename]['content_type']

        support = {
            'id': support_id,
            'name': doc.get('name'),
            'description': doc.get('description'),
            'file': base64.b64encode(attachment).decode('utf-8') if attachment else None,
            'filename': filename,
            'content_type': content_type,
        }

        return render(request, self.template_name, {'support': support})
