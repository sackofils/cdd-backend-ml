from django.urls import path

from dashboard.pending_actions import views

app_name = 'pending_actions'
urlpatterns = [
    path('', views.PendingActionsListView.as_view(), name='list'),
    path('pending-actions-list/', views.PendingActionsTableListView.as_view(), name='pending_actions_list'),
]