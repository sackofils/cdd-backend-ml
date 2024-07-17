from django.urls import path

from dashboard.supports import views

app_name = 'supports'
urlpatterns = [
    path('', views.SupportListView.as_view(), name='list'),
    path('supports-list/', views.SupportsListTableView.as_view(), name='supports_list'),
    path('create/', views.CreateSupportFormView.as_view(), name='create'),
    path('update/<str:support_id>/', views.UpdateSupportView.as_view(), name='update'),
    path('detail/<str:support_id>/', views.SupportDetailView.as_view(), name='detail'),
    path('delete/<str:id>', views.delete, name='delete'),
    path('download/<str:support_id>/<str:filename>/', views.SupportFileDownloadView.as_view(), name='download'),
]
