from django.urls import path

from dashboard.organism_type import views

app_name = 'organism_type'
urlpatterns = [
    path('', views.OrganismTypeListView.as_view(), name='list'),
    path('<int:pk>', views.OrganismTypeDetailView.as_view(), name='organism_detail'),
    path('organism-list/', views.OrganismTypeListTableView.as_view(), name='organism_list'),
    path('create-organism/', views.CreateOrganismTypeView.as_view(), name='create'),
    path('update-organism/<int:pk>', views.UpdateOrganismTypeView.as_view(), name='update'),
    path('delete-organism/<int:pk>', views.UpdateOrganismTypeView.as_view(), name='delete')
]