from django.contrib import admin
from .models import Phase, Project, Activity, Task, FormField, FormType


# Register your models here.


# Register your models here.
class BaseModelAdmin(admin.ModelAdmin):
    """
    Base class for model admins
    """
    readonly_fields = ('created_on', 'created_by', 'updated_on', 'updated_by', 'couch_id')


# exclude = ('created_on', 'created_by', 'updated_on', 'updated_by', 'couch_id')

class FormFieldInline(admin.TabularInline):
    """
    DocField handling for admin interface
    """
    model = FormField
    extra = 1


class FormTypeAdmin(BaseModelAdmin):
    """
    DocField handling for admin interface
    """
    # fieldsets = [(None, {'fields': ['name', 'description', 'couch_id']}),
    #             #  ('Fields', {'fields': []})
    #              ]
    inlines = [FormFieldInline]


admin.site.register(Project)
admin.site.register(Phase)
admin.site.register(Activity)
admin.site.register(Task)
admin.site.register(FormType, FormTypeAdmin)