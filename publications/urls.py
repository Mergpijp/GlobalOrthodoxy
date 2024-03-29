from django.urls import path, include, re_path

from .views import SearchResultsView, SearchResultsViewNew, render_search, PublicationCreate, PublicationUpdate,\
    PublicationDelete, PublicationDetailView, SearchResultsViewImages, PublicationDetailViewNew#, UploadedfileUpdateView
from . import views
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    path('get_countries/', views.get_countries, name='get-countries'),
    path('city_proces', views.city_proces, name='city-proces'),
    path('church_proces', views.church_proces, name='church-proces'),
    path('genre_proces', views.genre_proces, name='genre-proces'),
    path('occasion_prcoes', views.occasion_proces, name='occasion-proces'),
    path('ownedby_proces', views.ownedby_proces, name='ownedby-proces'),
    path('language_proces', views.proces_language, name='language-proces'),
    path('filecategory_proces', views.filecategory_proces, name='filecategory-proces'),
    path('form_of_publication_proces', views.proces_form_of_publication, name='form_of_publication-proces'),
    path('select2_filecategory/', views.filecategory_ajax, name='select2-filecategory'),
    path('nothing/', views.nothing, name='nothing'),
    path('gitlog/', include("gitlog.urls", namespace='gitlog')),
    path('uploadedfile_new/', views.UploadedFileCreateView.as_view(), name='uploadedfile_new'),
    #path('uploadedfile_new/None', views.PublicationUpdate.as_view(), name='uploadedfile_update'),
    path('uploadedfile_new/<int:pk>', views.UploadedFileCreateView.as_view(), name='uploadedfile_new'),
    #path('publication/new/<str:active_tab>/<int:object_id>', login_required(PublicationCreate.as_view()), name='publication-new'),
    #path(r'publication/new/(?P<active_tab>\w+)/(?P<object_id>\d+)$', login_required(PublicationCreate.as_view()), name='publication-new'),
    #path('publication/new/<str:ap><int:pk>', login_required(PublicationCreate.as_view()), name='publication-new'),
    path('publication/new/', login_required(PublicationCreate.as_view()), name='publication-new'),
    #path('publication/new/None', login_required(PublicationCreate.as_view()), name='publication-new'),
    path('detect_language', views.view_input_update, name='view-input-update'),
    path('search_uploaded_files/<int:pkb>', views.search_uploaded_files, name='search-uploaded-files'),
    path('search_files', views.search_files, name='search-files'),
    path('uploadedfiles/<int:pkb>', csrf_exempt(views.uploadedfiles), name='uploadedfiles'),
    path('link_file/<int:pkb>/<int:pk>', views.link_file, name='link-file'),
    path('unlink_file/<int:pkb>/<int:pk>', views.unlink_file, name='unlink-file'),

    path('search_translators/<int:pkb>', views.search_translators, name='search-translators'),
    path('search_authors/<int:pkb>', views.search_authors, name='search-authors'),
    path('authors/<int:pkb>', csrf_exempt(views.authors), name='authors'),
    path('translators/<int:pkb>', csrf_exempt(views.translators), name='translators'),
    path('link_author/<int:pkb>/<int:pk>', views.link_author, name='link-author'),
    path('unlink_author/<int:pkb>/<int:pk>', views.unlink_author, name='unlink-author'),
    path('link_translator/<int:pkb>/<int:pk>', views.link_translator, name='link-translator'),
    path('unlink_translator/<int:pkb>/<int:pk>', views.unlink_translator, name='unlink-translator'),
    path('author/proces/<int:pkb>/', views.process_author, name='author-proces'),
    path('author/proces/<int:pkb>/<int:pk>', views.process_author, name='author-proces'),
    path('translator/proces/<int:pkb>', views.process_translator, name='translator-proces'),
    path('translator/proces/<int:pkb>/<int:pk>', views.process_translator, name='translator-proces'),

    #path('url_replace', views.url_replace, name='url_replace'),
    path('uploadedfile/proces/<int:pk>', views.process_file, name='uploadedfile-proces'),
    path('uploadedfile/proces/<int:pk>/<int:pkb>', views.process_file, name='uploadedfile-proces'),
    path('uploadedfile/proces2/<int:pkb>', views.process_file2, name='uploadedfile-proces2'),
    path('uploadedfile/proces/', views.process_file, name='uploadedfile-proces'),
    path('publication/show/', login_required(SearchResultsView.as_view()), name='publication-show'),
    path('researcher/', login_required(SearchResultsView.as_view()), name='publication-show'),
    path('new/grid/', SearchResultsViewImages.as_view(), name='images'),
    path('publication/<int:pk>/detail_view/', PublicationDetailView.as_view(), name='publication-detail'),
    path('publication/<int:pk>/public/', PublicationDetailViewNew.as_view(), name='publication-detail-new'),
    #path('publication/<int:pk>/detail_view/', login_required(PublicationDetailView.as_view()), name='publication-detail'),
    path('publication/<int:pk>/edit/', login_required(PublicationUpdate.as_view()), name='publication-update'),
    path('publication/<int:pk>/delete/', PublicationDelete, name='publication-delete'),
    path('thrashbin/show/', login_required(views.ThrashbinShow.as_view()), name='thrashbin-show'),
    path('thrashbin/uploadedfile/show/', login_required(views.ThrashbinUploadedFileShow.as_view()), name='thrashbin-uploadedfile-show'),
    path('publication/<int:pk>/restore/', views.ThrashbinRestore, name='thrashbin-restore'),
    path('uploadedfile/<int:pk>/restore/', views.ThrashbinUploadedFileRestore, name='thrashbin-restore'),
    path('author/new/', login_required(views.AuthorCreate.as_view()), name='author-new'),
    path('author/show/', login_required(views.AuthorShow.as_view()), name='author-show'),
    path('author/<int:pk>/edit/', login_required(views.AuthorUpdate.as_view()), name='author-update'),
    path('author/<int:pk>/edit/close', login_required(views.AuthorUpdate.as_view()), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete, name='author-delete'),    
    path('translator/new/', login_required(views.TranslatorCreate.as_view()), name='translator-new'),
    path('translator/show/', login_required(views.TranslatorShow.as_view()), name='translator-show'),
    path('translator/<int:pk>/edit/', login_required(views.TranslatorUpdate.as_view()), name='translator-update'),
    path('translator/<int:pk>/edit/close', login_required(views.TranslatorUpdate.as_view()), name='translator-update'),
    path('translator/<int:pk>/delete/', views.TranslatorDelete, name='translator-delete'), 
    path('form_of_publication/new/', login_required(views.FormOfPublicationCreate.as_view()), name='form-of-publication-new'),
    path('form_of_publication/show/', login_required(views.FormOfPublicationShow.as_view()), name='form-of-publication-show'),
    path('form_of_publication/<int:pk>/edit/', login_required(views.FormOfPublicationUpdate.as_view()), name='form-of-publication-update'),
    path('form_of_publication/<int:pk>/delete/', views.FormOfPublicationDelete, name='form-of-publlication-delete'),    
    path('city/new/', login_required(views.CityCreate.as_view()), name='city-new'),
    path('city/show/', login_required(views.CityShow.as_view()), name='city-show'),
    path('city/<int:pk>/edit/', login_required(views.CityUpdate.as_view()), name='city-update'),
    path('city/<int:pk>/delete/', views.CityDelete, name='city-delete'),    
    path('genre/new/', login_required(views.GenreCreate.as_view()), name='genre-new'),
    path('genre/show/', login_required(views.GenreShow.as_view()), name='genre-show'),
    path('genre/<int:pk>/edit/', login_required(views.GenreUpdate.as_view()), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete, name='genre-delete'),    
    path('church/new/', login_required(views.ChurchCreate.as_view()), name='church-new'),
    path('church/show/', login_required(views.ChurchShow.as_view()), name='church-show'),
    path('church/<int:pk>/edit/', login_required(views.ChurchUpdate.as_view()), name='church-update'),
    path('church/<int:pk>/delete/', views.ChurchDelete, name='church-delete'), 
    path('language/new/', login_required(views.LanguageCreate.as_view()), name='language-new'),
    path('language/show/', login_required(views.LanguageShow.as_view()), name='language-show'),
    path('language/<int:pk>/edit/', login_required(views.LanguageUpdate.as_view()), name='language-update',),
    path('language/<int:pk>/delete/', views.LanguageDelete, name='language-delete'), 
    path('special_occasion/new/', login_required(views.SpecialOccasionCreate.as_view()), name='special-occasion-new'),
    path('special_occasion/show/', login_required(views.SpecialOccasionShow.as_view()), name='special-occasion-show'),
    path('special_occasion/<int:pk>/edit/', login_required(views.SpecialOccasionUpdate.as_view()), name='special-occasion-update',),
    path('special_occasion/<int:pk>/delete/', views.SpecialOccasionDelete, name='special-occasion-delete'),
    path('owner/new/', login_required(views.OwnerCreate.as_view()), name='owner-new'),
    path('owner/show/', login_required(views.OwnerShow.as_view()), name='owner-show'),
    path('owner/<int:pk>/edit/', login_required(views.OwnerUpdate.as_view()), name='owner-update',),
    path('owner/<int:pk>/delete/', views.OwnerDelete, name='owner-delete'),
    path('keyword/new/', login_required(views.KeywordCreate.as_view()), name='keyword-new'),
    path('keyword/show/', login_required(views.KeywordShow.as_view()), name='keyword-show'),
    path('keyword/<int:pk>/edit/', login_required(views.KeywordUpdate.as_view()), name='keyword-update'),
    path('keyword/<int:pk>/delete/', views.KeywordDelete, name='keyword-delete'),
    path('uploadedfile/new/', login_required(views.UploadedFileCreate.as_view()), name='uploadedfile-new'),
    path('uploadedfile/show/', login_required(views.UploadedFileShow.as_view()), name='uploadedfile-show'),
    path('uploadedfile/<int:pk>/edit/', login_required(views.UploadedFileUpdate.as_view()), name='uploadedfile-update',),
    path('uploadedfile/<int:pk>/edit/close', login_required(views.UploadedFileUpdate.as_view()), name='uploadedfile-update',),
    path('uploadedfile/<int:pk>/delete/', views.UploadedFileDelete, name='uploadedfile-delete'),
    path('filecategory/new/', login_required(views.FileCategoryCreate.as_view()), name='filecategory-new'),
    path('filecategory/show/', login_required(views.FileCategoryShow.as_view()), name='filecategory-show'),
    path('filecategory/<int:pk>/edit/', login_required(views.FileCategoryUpdate.as_view()), name='filecategory-update',),
    path('filecategory/<int:pk>/delete/', views.FileCategoryDelete, name='filecategory-delete'),
    path('', SearchResultsViewImages.as_view(), name='images'),

    path('publications/', SearchResultsViewNew.as_view(), name='publication-show-new'),
    path('churches/', views.ChurchShowNew.as_view(), name='churches-show-new'),
    path('languages/', views.LanguageShowNew.as_view(), name='languages-show-new'),
    path('authors/', views.AuthorShow.as_view(), name='authors-show-new'),
    path('filecategories/', views.FileCategoryShow.as_view(), name='filecategories-show-new'),
    path('form_of_publications/', views.FormOfPublicationShow.as_view(), name='authors-show-new'),
    path('genres/', views.GenreShow.as_view(), name='genres-show-new'),
    path('keywords/', views.KeywordShow.as_view(), name='keywords-show-new'),
    path('cities/', views.CityShow.as_view(), name='cities-show-new'),
    path('specialoccasions/', views.SpecialOccasionShow.as_view(), name='specialoccasions-show-new'),
    path('translators/', views.TranslatorShow.as_view(), name='translators-show-new'),
    path('uploadedfiles/', views.UploadedFileShow.as_view(), name='uploadedfiles-show-new'),
    path('spacetime/', views.SpaceTimeSearch.as_view(), name='space-time-search'),

    path('about/', views.about, name='about')
]