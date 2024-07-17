from django.urls import path

from dashboard.organism import views

app_name = 'organisms'
urlpatterns = [
    path('', views.OrganismListView.as_view(), name='list'),
    path('<int:pk>', views.OrganismDetailView.as_view(), name='organism_detail'),
    path('organism-list/', views.OrganismListTableView.as_view(), name='organism_list'),
    path('create-organism/', views.CreateOrganismView.as_view(), name='create'),
    path('update-organism/<int:pk>', views.UpdateOrganismView.as_view(), name='update'),
    path('delete-organism/<int:pk>', views.UpdateOrganismView.as_view(), name='delete')
]