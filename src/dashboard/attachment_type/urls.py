from django.urls import path

from dashboard.attachment_type import views

app_name = 'attachment_type'
urlpatterns = [
    path('', views.AttachmentTypeListView.as_view(), name='list'),
    path('<int:pk>', views.AttachmentTypeDetailView.as_view(), name='attachment_detail'),
    path('attachment-list/', views.AttachmentTypeListTableView.as_view(), name='attachment_list'),
    path('create-attachment/', views.CreateAttachmentTypeView.as_view(), name='create'),
    path('update-attachment/<int:pk>', views.UpdateAttachmentTypeView.as_view(), name='update'),
    path('delete-attachment/<int:pk>', views.UpdateAttachmentTypeView.as_view(), name='delete')
]