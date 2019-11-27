from django.urls import path, include

from . import views
from .views import HomePageView, SearchResultsView

urlpatterns = [
    #path('', views.index, name='index'),
    #path('<int:publication_id>/', views.detail, name='detail'),
    #path('publications/new/', views.publication_new, name='publication_new'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    #path('', HomePageView.as_view(), name='home'),
    path('', views.get_name, name='index'),
    #path(r'^chaining/', include('smart_selects.urls')),
]