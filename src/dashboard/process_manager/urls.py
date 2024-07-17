from django.urls import path

from dashboard.process_manager import views

app_name = 'process_manager'
urlpatterns = [
    path('get-choices-for-next-phases-activities-tasks', views.GetChoicesForNextPhaseActivitiesTasksView.as_view(),
         name='get_choices_for_next_phases_activities_tasks'),
    path('get-choices-for-next-phases-activities-tasks-by-id', views.GetChoicesForNextPhaseActivitiesTasksByIdView.as_view(),
         name='get_choices_for_next_phases_activities_tasks_by_id'),
     path('validate_invalidate-task', views.ValidateTaskView.as_view(), name='validate_invalidate_task'),
     path('complete-uncomplete-task', views.CompleteTaskView.as_view(), name='complete_uncomplete_task'),
]
