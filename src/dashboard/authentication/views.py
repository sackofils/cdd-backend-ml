from django.shortcuts import render, redirect
from rest_framework import status
from django.utils.translation import gettext_lazy
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.mixins import PageMixin
from authentication.permissions import AdminPermissionRequiredMixin
from dashboard.authentication.forms import CreateUserForm, UpdateUserForm
from django.contrib.auth.models import User, Group, Permission
from django.forms.models import model_to_dict
from django.contrib import messages
from django.http import Http404
from authentication.models import Profile, Organism


def handler400(request, exception):
    return render(
        request,
        template_name='common/400.html',
        status=status.HTTP_400_BAD_REQUEST,
        content_type='text/html'
    )


def handler403(request, exception):
    return render(
        request,
        template_name='common/403.html',
        status=status.HTTP_403_FORBIDDEN,
        content_type='text/html'
    )


def handler404(request, exception):
    return render(
        request,
        template_name='common/404.html',
        status=status.HTTP_404_NOT_FOUND,
        content_type='text/html'
    )


def handler500(request):
    return render(
        request,
        template_name='common/500.html',
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content_type='text/html'
    )


class UsersListView(PageMixin, LoginRequiredMixin, generic.ListView):
    """Display user list"""

    model = User
    template_name = 'authentication/users.html'
    context_object_name = 'users'
    title = gettext_lazy('Users')
    active_level1 = 'users'
    breadcrumb = [
        {
            'url': '',
            'title': title
        },
    ]


class CreateUpdateUserFormView(PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.FormView):
    template_name = 'authentication/create.html'
    title = gettext_lazy('Create User')
    active_level1 = 'users'
    form_class = CreateUserForm
    success_url = reverse_lazy('dashboard:authentication:users')
    breadcrumb = [
        {
            'url': reverse_lazy('dashboard:authentication:users'),
            'title': gettext_lazy('Users')
        },
        {
            'url': '',
            'title': title
        }
    ]
    id = 0

    def dispatch(self, request, *args, **kwargs):
        try:
            self.id = kwargs['id']
        except Exception:
            pass
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CreateUpdateUserFormView, self).get_context_data(**kwargs)
        if self.id:
            form = UpdateUserForm(instance=User.objects.get(id=self.id))
            ctx['form'] = form

            ctx['title'] = gettext_lazy('Update User')
            ctx['breadcrumb'] = [
                {
                    'url': reverse_lazy('dashboard:authentication:users'),
                    'title': gettext_lazy('Users')
                },
                {
                    'url': '',
                    'title': ctx['title']
                }
            ]

        return ctx

    def post(self, request, *args, **kwargs):
        if self.id:
            form = UpdateUserForm(request.POST, instance=User.objects.get(id=self.id))
        else:
            form = CreateUserForm(request.POST)

        if form.is_valid():
            groups = form.cleaned_data['groups']
            # user_permissions = form.cleaned_data['user_permissions']
            try:
                for g in groups:
                    Group.objects.get(name=g.name)
                # for u_p in user_permissions:
                #    Permission.objects.get(name=u_p.name)
            except Exception as exc:
                messages.info(request, gettext_lazy(exc.__str__()))
                return super(CreateUpdateUserFormView, self).get(request, *args, **kwargs)

            instance = form.save()
            if form.cleaned_data['organism']:
                organism = Organism.objects.get(acronym=form.cleaned_data['organism'])
                instance.user_profile.organism = organism
                instance.user_profile.save()

            return redirect('dashboard:authentication:users')
        return super(CreateUpdateUserFormView, self).get(request, *args, **kwargs)


class DeleteUserFormView(PageMixin, LoginRequiredMixin, AdminPermissionRequiredMixin, generic.TemplateView):
    template_name = 'authentication/delete.html'
    title = gettext_lazy('Delete User')
    active_level1 = 'users'
    success_url = reverse_lazy('dashboard:authentication:users')
    breadcrumb = [
        {
            'url': reverse_lazy('dashboard:authentication:users'),
            'title': gettext_lazy('Users')
        },
        {
            'url': '',
            'title': title
        }
    ]

    id = 0

    def dispatch(self, request, *args, **kwargs):
        try:
            self.id = kwargs['id']
        except Exception:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DeleteUserFormView, self).get_context_data(**kwargs)
        try:
            if self.id:
                ctx['object'] = User.objects.get(id=self.id)
            return ctx
        except Exception as exc:
            messages.info(self.request, gettext_lazy(exc.__str__()))
            return redirect('dashboard:authentication:users')

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=self.id)
            user.delete()
            return redirect('dashboard:authentication:users')
        except Exception as exc:
            messages.info(request, gettext_lazy(exc.__str__()))

        return super(DeleteUserFormView, self).get(request, *args, **kwargs)
