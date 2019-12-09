from django.urls import path, include

from .views import SearchResultsView, render_search, publication_new, PublicationCreate, PublicationUpdate, PublicationDelete

urlpatterns = [
    #path('', views.index, name='index'),
    # #path('<int:publication_id>/', views.detail, name='detail'),
    path('publications/new/', PublicationCreate.as_view(), name='publication-new'),
    path('publication/<int:pk>/', PublicationUpdate.as_view(), name='publication-update'),
    path('publication/<int:pk>/delete/', PublicationDelete.as_view(), name='publiaction-delete'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    # #path('', HomePageView.as_view(), name='home'),
    path('', render_search, name='index'),
]