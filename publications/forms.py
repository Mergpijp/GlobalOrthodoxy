from django import forms

from .models import Publication, Author, Translator, FormOfPublication, Genre, Church, SpecialOccasion, Owner, City, \
    Language, IllustrationLayoutType, UploadedFile, Keyword, FileCategory, ImageContent
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Field, Button, HTML
from crispy_forms.bootstrap import Tab, TabHolder, FieldWithButtons, StrictButton, AppendedText
from django.forms.models import inlineformset_factory
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget, ModelSelect2TagWidget, \
    Select2Widget, ModelSelect2Widget, HeavySelect2MultipleWidget, ModelSelect2TagWidget
# from django_countries.fields import CountryField
# from django_countries import countries
from django_countries.widgets import CountrySelectWidget
from countries_plus.models import Country
from django.utils.encoding import force_text
from bootstrap_modal_forms.forms import BSModalModelForm


class UploadedfileWidget(ModelSelect2Widget):
    search_fields = [
        "image_title__icontains",
    ]


class PublicationForm(forms.ModelForm):
    '''
    This is a search form.
    All select2 fields are defined so that they load content dynamically.
    Crispy forms is used with layout object for the layout.
    All many-to-many fields are not required.
    The button is a search button instead of a submit button.
    
    '''
    authors = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Author,
        search_fields=['name__icontains'],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Author.objects.all(), required=False)
    translators = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Translator,
        search_fields=['name__icontains'],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Translator.objects.all(), required=False)
    form_of_publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=FormOfPublication,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=FormOfPublication.objects.all(), required=False)
    publication_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label=u"Publication Country",
        widget=ModelSelect2Widget(
            model=Country,
            search_fields=['name__icontains'],
            attrs={'data-minimum-input-length': 0},
            dependent_fields={'publication_city': 'cities'},
        )
    )
    publication_city = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=City,
        search_fields=['name__icontains', ],
        dependent_fields={'publication_country': 'country'},
        attrs={'data-minimum-input-length': 0},
    ), queryset=City.objects.all(), required=False)
    affiliated_church = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Church,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Church.objects.all(), required=False)
    language = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Language,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Language.objects.all(), required=False)
    content_genre = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Genre,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Genre.objects.all(), required=False)
    connected_to_special_occasion = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=SpecialOccasion,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=SpecialOccasion.objects.all(), required=False)
    collection_country = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=Country,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Country.objects.all(), required=False)
    currently_owned_by = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Owner,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Owner.objects.all(), required=False)
    uploadedfiles = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=UploadedFile,
        search_fields=['image_title__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=UploadedFile.objects.all(), required=False)
    keywords = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Keyword,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Keyword.objects.all(), required=False)
    translated_from = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=Language,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Language.objects.all(), required=False)

    class Meta:
        model = Publication
        fields = ('title', 'title_subtitle_transcription', 'title_translation', 'authors', 'translators', \
                  'form_of_publication', 'editor', 'printed_by', 'published_by', 'publication_year',
                  'publication_country', 'publication_city', 'publishing_organisation', \
                  'donor', 'affiliated_church', 'extra_info', 'language', 'content_description', 'content_genre',
                  'connected_to_special_occasion', 'description_of_illustration', \
                  'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights',
                  'currently_owned_by', 'contact_telephone_number', \
                  'contact_email', 'contact_website', 'general_comments', 'team_comments', 'uploadedfiles', 'keywords',
                  'is_a_translation', 'ISBN_number', 'translated_from')

    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['authors'].required = False
        self.fields['translators'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['publication_city'].required = False
        self.fields['affiliated_church'].required = False
        self.fields['language'].required = False
        self.fields['content_genre'].required = False
        self.fields['connected_to_special_occasion'].required = False
        self.fields['currently_owned_by'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['uploadedfiles'].required = False
        self.fields['publication_country'].required = False
        self.fields['collection_country'].required = False
        self.fields['is_a_translation'].required = False
        self.fields['keywords'].required = False
        self.fields['translated_from'].required = False

        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'

        self.helper.layout = Layout(
            TabHolder(
                Tab('Titles',
                    'title',
                    'title_subtitle_transcription',
                    'title_translation',

                    ),
                Tab('Author',
                    'authors',
                    'translators',
                    'is_a_translation',
                    'translated_from',
                    'editor',
                    ),
                Tab('Language',
                    'language',
                    ),
                Tab('Publishing information',
                    'form_of_publication',
                    'ISBN_number',
                    'printed_by',
                    'published_by',
                    'publication_year',
                    'publication_country',
                    'publication_city',
                    'publishing_organisation',
                    ),
                Tab('Affiliation',
                    'donor',
                    'affiliated_church',
                    'extra_info',
                    ),
                Tab('Content',
                    'content_description',
                    'content_genre',
                    'connected_to_special_occasion',
                    'description_of_illustration',
                    'nr_of_pages',
                    'keywords',
                    ),
                Tab('Collection info',
                    'collection_date',
                    'collection_country',
                    'collection_venue_and_city',
                    'copyrights',
                    'currently_owned_by',
                    'contact_telephone_number',
                    'contact_email',
                    'contact_website',
                    ),
                Tab('Files',
                    'uploadedfiles',

                    ),
                Tab('Comments',
                    'general_comments',
                    'team_comments',
                    )
            ),
            ButtonHolder(
                Submit('search', 'Search', css_class='btn-danger')
            )
        )


def represent_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class KeywordSelect2TagWidget(ModelSelect2TagWidget):
    queryset = Keyword.objects.all()

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if isinstance(values, str):
            values = values.split(sep=',')
        queryset = self.get_queryset()
        pks = queryset.filter(**{'pk__in': [v for v in values if v.isdigit()]}).values_list('pk', flat=True)
        cleaned_values = []
        for val in values:
            if represent_int(val) and int(val) not in pks or not represent_int(val) and force_text(val) not in pks:
                val = queryset.create(name=val).pk
            cleaned_values.append(val)
        return cleaned_values


class ImageContentSelect2TagWidget(ModelSelect2TagWidget):
    queryset = ImageContent.objects.all()

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        if isinstance(values, str):
            values = values.split(sep=',')
        queryset = self.get_queryset()
        if values:
            pks = queryset.filter(**{'pk__in': [v for v in values if v.isdigit()]}).values_list('pk', flat=True)
        cleaned_values = []
        if values:
            for val in values:
                if represent_int(val) and int(val) not in pks or not represent_int(val) and force_text(val) not in pks:
                    val = queryset.create(name=val).pk
                cleaned_values.append(val)
        return cleaned_values


class NewCrispyForm(forms.ModelForm):
    '''
        Crispy form for publication create/update(edit).
        Added field with buttons for inline add. Is almost the same as PublicationForm but has a submit button.

    '''
    authors = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Author,
        search_fields=['name__icontains'],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Author.objects.all(), required=False)
    translators = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Translator,
        search_fields=['name__icontains'],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Translator.objects.all(), required=False)
    form_of_publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=FormOfPublication,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=FormOfPublication.objects.all(), required=False)
    publication_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label=u"Publication Country",
        widget=ModelSelect2Widget(
            model=Country,
            search_fields=['name__icontains'],
            attrs={'data-minimum-input-length': 0},
            dependent_fields={'publication_city': 'cities'},
        )
    )
    publication_city = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=City,
        search_fields=['name__icontains', ],
        dependent_fields={'publication_country': 'country'},
        attrs={'data-minimum-input-length': 0},
    ), queryset=City.objects.all(), required=False)
    affiliated_church = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Church,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Church.objects.all(), required=False)
    language = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Language,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Language.objects.all(), required=False)
    content_genre = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Genre,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Genre.objects.all(), required=False)
    connected_to_special_occasion = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=SpecialOccasion,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=SpecialOccasion.objects.all(), required=False)
    collection_country = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=Country,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Country.objects.all(), required=False)
    currently_owned_by = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Owner,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Owner.objects.all(), required=False)
    keywords = forms.ModelMultipleChoiceField(widget=KeywordSelect2TagWidget(
        model=Keyword,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0, "data-token-separators": '[";"]', },
    ), queryset=Keyword.objects.all(), required=False)
    uploadedfiles = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=UploadedFile,
        search_fields=['description__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=UploadedFile.objects.all(), required=False)
    translated_from = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=Language,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=Language.objects.all(), required=False)
    '''
    def clean_uploadedfiles(self):
        uploadedfiles = self.cleaned_data['uploadedfiles']
        return uploadedfiles
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['authors'].required = False
        self.fields['translators'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['publication_city'].required = False
        self.fields['affiliated_church'].required = False
        self.fields['language'].required = False
        self.fields['content_genre'].required = False
        self.fields['connected_to_special_occasion'].required = False
        self.fields['currently_owned_by'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['uploadedfiles'].required = False
        self.fields['publication_country'].required = False
        self.fields['is_a_translation'].required = False
        self.fields['keywords'].required = False
        self.fields['translated_from'].required = False

        self.helper.layout = Layout(
            TabHolder(
                Tab('Titles',
                    'title',
                    'title_subtitle_transcription',
                    'title_translation',
                    Div('title2', 'title_subtitle_transcription2', 'title_translation2', css_class="hidden"),
                    Div('title3', 'title_subtitle_transcription3', 'title_translation3', css_class="hidden"),
                    Div('title4', 'title_subtitle_transcription4', 'title_translation4', css_class="hidden"),
                    Div('title5', 'title_subtitle_transcription5', 'title_translation5', css_class="hidden"),
                    Button('titles', 'Add more titles', css_class='btn-back btn-danger',
                           onclick="$('.hidden:first').removeClass('hidden');"),
                    ),
                Tab('Author',
                    HTML("""{% include "_author_translator.html" %}"""),
                    'is_a_translation',
                    FieldWithButtons('translated_from', StrictButton('+', type='button', css_class='btn-danger',
                                                                     onClick="window.open('/language/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'editor',
                    ),
                Tab('Language',
                    FieldWithButtons('language', StrictButton('+', type='button', css_class='btn-danger',
                                                              onClick="window.open('/language/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    ),
                Tab('Publishing information',
                    FieldWithButtons('form_of_publication', StrictButton('+', type='button', css_class='btn-danger',
                                                                         onClick="window.open('/form_of_publication/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'ISBN_number',
                    'printed_by',
                    'published_by',
                    'publication_year',
                    'publication_country',
                    FieldWithButtons('publication_city', StrictButton('+', type='button', css_class='btn-danger',
                                                                      onClick="window.open('/city/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'publishing_organisation',
                    'currency',
                    'price',
                    ),
                Tab('Affiliation',
                    'donor',
                    FieldWithButtons('affiliated_church', StrictButton('+', type='button', css_class='btn-danger',
                                                                       onClick="window.open('/church/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'extra_info',
                    ),
                Tab('Content',
                    'content_description',
                    FieldWithButtons('content_genre', StrictButton('+', type='button', css_class='btn-danger',
                                                                   onClick="window.open('/genre/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    FieldWithButtons('connected_to_special_occasion',
                                     StrictButton('+', type='button', css_class='btn-danger',
                                                  onClick="window.open('/special_occasion/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'description_of_illustration',
                    'nr_of_pages',
                    Field('keywords', css_class='special_select2'),
                    ),
                Tab('Collection info',
                    'collection_date',
                    'collection_country',
                    'collection_venue_and_city',
                    'collection_context',
                    'copyrights',
                    FieldWithButtons('currently_owned_by', StrictButton('+', type='button', css_class='btn-danger',
                                                                        onClick="window.open('/owner/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'contact_telephone_number',
                    'contact_email',
                    'contact_website',
                    ),
                #HTML("""<div id=files class ="tab-pane {% if active_tab == 'tab-files' %} active{% endif %}"> """,#Tab('Files',

            Tab('Files',
                HTML("""{% include "_uploadedfile.html" %}"""),
                css_id="files",
                ),

                Tab('Comments',
                    'general_comments',
                    'team_comments',
                    'other_comments',
                    ),
            ),
            ButtonHolder(
                #Button('cancel', 'Back', css_class='btn-back btn-danger', onclick="history.back()"),
                #Submit('next', 'Next', css_class='btn-danger'),
                Submit('save', 'Save', css_class='btn-save btn-danger'),
            )
        )

    def clean(self):
        if 'Save' in self.data:
            print('in')

    # do unsubscribe
    class Meta:
        model = Publication
        # See note here: https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
        fields = ('title', 'title_subtitle_transcription', 'title_translation', 'title2',
                  'title_subtitle_transcription2', 'title_translation2', 'authors', 'translators', \
                  'form_of_publication', 'editor', 'printed_by', 'published_by', 'publication_year',
                  'publication_country', 'publication_city', 'publishing_organisation', \
                  'donor', 'affiliated_church', 'extra_info', 'language', 'content_description', 'content_genre',
                  'connected_to_special_occasion', 'description_of_illustration', \
                  'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights',
                  'currently_owned_by', 'contact_telephone_number', \
                  'contact_email', 'contact_website', 'general_comments', 'team_comments', 'other_comments', 'keywords',
                  'is_a_translation', 'ISBN_number', 'translated_from', \
                  'title3', 'title_subtitle_transcription3', 'title_translation3', 'title4',
                  'title_subtitle_transcription4', 'title_translation4', \
                  'title5', 'title_subtitle_transcription5', 'title_translation5', 'price', 'collection_context', \
                  'currency')
        exclude = ('uploadedfiles',)
        # publication_country = forms.ChoiceField(choices=list(countries))

import pdb

class KeywordForm(forms.ModelForm):
    '''
        Form to create or edit an author. Can add Publications to the to be created author object.
        If its a keyword edit load all linked publications.
        If its a keyword create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Keyword
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class FileCategoryForm(forms.ModelForm):
    '''
        Form to create or edit an filecategory.
        If its a FileCategory edit load all linked uploadedfiles.
        If its a FileCategory create do not load any uploadedfiles at start.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'order_index', 'list_view_priority',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = FileCategory
        fields = ('name', 'order_index', 'list_view_priority')

    def save(self, commit=True):
        instance = super().save(commit)
        return instance

class ImageContentForm(forms.ModelForm):
    '''
        Form to create or edit an ImageContent.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = ImageContent
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance

class AuthorForm(forms.ModelForm):
    '''
        Form to create or edit an author. Can add Publications to the to be created author object.
        If its a author edit load all linked publications.
        If its a author create do not load any publications at start.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'name_original_language', 'extra_info',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Author
        fields = ('name', 'name_original_language', 'extra_info')

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class TranslatorForm(forms.ModelForm):
    '''
        Form to create or edit an translator. Can add Publications to the to be created translator object.
        If its a translator edit load all linked publications.
        If its a translator create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'name_original_language', 'extra_info', 'publication',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Translator
        fields = ('name', 'name_original_language', 'extra_info',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class FormOfPublicationForm(forms.ModelForm):
    '''
        Form to create or edit an form of publication. Can add Publications to the to be created form of publication object.
        If its a form of publication edit load all linked publications.
        If its a form of publication create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = FormOfPublication
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class CityForm(forms.ModelForm):
    '''
        Form to create or edit an city. Can add Publications to the to be created city object.
        If its a city edit load all linked publications.
        If its a city create do not load any publications at start.
    '''
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label=u"Country",
        widget=ModelSelect2Widget(
            model=Country,
            attrs={'data-minimum-input-length': 0},
            search_fields=['name__icontains'],
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'country',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = City
        fields = ('name', 'country',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class ChurchForm(forms.ModelForm):
    '''
        Form to create or edit an church. Can add Publications to the to be created church object.
        If its a church edit load all linked publications.
        If its a church create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Church
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class LanguageForm(forms.ModelForm):
    '''
        Form to create or edit an language. Can add Publications to the to be created language object.
        If its a language edit load all linked publications.
        If its a language create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'direction',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Language
        fields = ('name', 'direction',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class GenreForm(forms.ModelForm):
    '''
        Form to create or edit an genre. Can add Publications to the to be created genre object.
        If its a genre edit load all linked publications.
        If its a genre create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Genre
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class SpecialOccasionForm(forms.ModelForm):
    '''
        Form to create or edit an special occasion. Can add Publications to the to be created special occasion object.
        If its a special occasion edit load all linked publications.
        If its a special occasion create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = SpecialOccasion
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class OwnerForm(forms.ModelForm):
    '''
        Form to create or edit an owner. Can add Publications to the to be created owner object.
        If its a owner edit load all linked publications.
        If its a owner create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = Owner
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance


class UploadedFileForm(forms.ModelForm):
    '''
        Form to create or edit an uploaded file. Can add Publications to the to be created uploaded file object.
        If its a uploaded file edit load all linked publications.
        If its a uploaded file create do not load any publications at start.
    '''

    image_contents = forms.ModelMultipleChoiceField(widget=ImageContentSelect2TagWidget(
        model=ImageContent,
        search_fields=['name__icontains' ],
        attrs={'data-minimum-input-length': 0, "data-token-separators": '[";"]'},
    ), queryset=ImageContent.objects.all(), required=False)
    '''
    imagecontents = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=ImageContent,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=ImageContent.objects.all(), required=False)
    '''
    filecategory = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=FileCategory,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=FileCategory.objects.all(), required=False)
    '''
    publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        attrs={'data-minimum-input-length': 0},
        search_fields=['title_subtitle_European__icontains', 'title__icontains',
                       'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        if self.instance.id:
            self.fields['publication'].initial = Publication.objects.filter(uploadedfiles=self.instance)
        '''
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-dropzoneform'
        self.helper.form_class = 'dropzone-form'
        self.helper.layout = Layout(
            'image_title',
            FieldWithButtons('filecategory', StrictButton('+', type='button', css_class='btn-danger',
                                                             onClick="window.open('/filecategory/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
            'image_contents',
            #FieldWithButtons('imagecontents', StrictButton('+', type='button', css_class='btn-danger',
            #                                                 onClick="window.open('/imagecontent/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
            HTML("""
                                        File
                                        <div id='my-drop-zone' class='needsclick'>
                                            <div class="dz-message needsclick"> 
                                                Drop file here or click to upload.
                                            </div>
                                        </div>
                                        <br/>
                                    """),
            ButtonHolder(
                Submit('Submit', 'Submit', css_class='btn-danger', css_id='submit-btn')),
            HTML("""
                                        <script>
                                            {% if object %}
                                            var pk = {{object.id}} ;
                                            {% else %}
                                            var pk = ""
                                            {% endif %}
                                            Dropzone.autoDiscover = false;
                                            var myDropzone = new Dropzone("div#my-drop-zone", { 
                                                url: "/uploadedfile/proces/" + pk,
                                                method: "post",
                                                autoProcessQueue: false,
                                                maxFiles: 1,
                                                addRemoveLinks: true,
                                                maxfilesexceeded: function(file) {
                                                    this.removeAllFiles();
                                                    this.addFile(file);
                                                },
                                                init: function () {
                                                    var myDropzone = this;
                                                    var addButton = $("#submit-btn");
                                                    addButton.click(function (e) {
                                                    if (myDropzone.getQueuedFiles().length > 0) {
                                                        e.preventDefault();
                                                        myDropzone.processQueue();
                                                    }
                                                    });
                                                },
                                                sending: function (file, xhr, formData) {
                                                    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
                                                    formData.append("image_title", $('#id_image_title').val());
                                                    formData.append('filecategory', $('#id_filecategory').val());
                                                    formData.append('image_contents', $('#id_image_contents').val());
                                                    
                                                    setTimeout(function () {
                                                            window.location.href='/uploadedfile/show/';
                                                    }, 2000);

                                                }
                                            });
                                            function getCookie(name) {
                                                var cookieValue = null;
                                                if (document.cookie && document.cookie != '') {
                                                    var cookies = document.cookie.split(';');
                                                    for (var i = 0; i < cookies.length; i++) {
                                                        var cookie = jQuery.trim(cookies[i]);
                                                        // Does this cookie string begin with the name we want?
                                                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                                            break;
                                                        }
                                                    }
                                                }
                                                return cookieValue;
                                            }
                                            $("#my-drop-zone").addClass("dropzone");
                                              Dropzone.options.myDropZone = {
                                                maxFilesize: 500,
                                                init: function() {
                                                  this.on("uploadprogress", function(file, progress) {
                                                    console.log("File progress", progress);
                                                  });
                                                }
                                              }
                                        </script>
                                        """),

        )

    class Meta:
        model = UploadedFile
        fields = ('image_title', 'filecategory', 'file', 'image_contents',)

    def save(self, commit=True):
        instance = super().save(commit)
        '''
        for pub in instance.publication_set.all():
            instance.publication_set.remove(pub)
        for pub in self.cleaned_data['publication'].all():
            instance.publication_set.add(pub)
        '''
        return instance

class UploadedFileModelForm2(BSModalModelForm):
    class Meta:
        model = UploadedFile
        fields = ('image_title', 'filecategory', 'file', 'image_contents',)

class UploadedFileModelForm(BSModalModelForm):

    image_contents = forms.ModelMultipleChoiceField(widget=ImageContentSelect2TagWidget(
        model=ImageContent,
        search_fields=['name__icontains' ],
        attrs={'data-minimum-input-length': 0, "data-token-separators": '[";"]' },
    ), queryset=ImageContent.objects.all(), required=False)
    '''
    image_contents = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=ImageContent,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0},
    ), queryset=ImageContent.objects.all(), required=False)
    '''
    filecategory = forms.ModelChoiceField(widget=ModelSelect2Widget(
        model=FileCategory,
        search_fields=['name__icontains', ],
        attrs={'data-minimum-input-length': 0  },
    ), queryset=FileCategory.objects.all(), required=False)
    '''
    publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        attrs={'data-minimum-input-length': 0},
        search_fields=['title_subtitle_European__icontains', 'title__icontains',
                       'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        if self.instance.id:
            self.fields['publication'].initial = Publication.objects.filter(uploadedfiles=self.instance)
        '''
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-dropzoneform'
        self.helper.form_class = 'dropzone-form'
        self.helper.layout = Layout(
            'image_title',
            FieldWithButtons('filecategory', StrictButton('+', type='button', css_class='btn-danger',
                                                          onClick="window.open('/filecategory/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
            'image_contents',
            # FieldWithButtons('imagecontents', StrictButton('+', type='button', css_class='btn-danger',
            #                                                 onClick="window.open('/imagecontent/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
            HTML("""
                                        File
                                        <div id='my-drop-zone' class='needsclick'>
                                            <div class="dz-message needsclick"> 
                                                Drop file here or click to upload.
                                            </div>
                                        </div>
                                        <br/>
                                    """),
            #ButtonHolder(
            #    Submit('Submit', 'Submit', css_class='btn-danger', css_id='submit-btn')),
            HTML("""
                                        <script>
                                            {% if pkb %}
                                            var pkb = {{pkb}} + "/";
                                            {% else %}
                                            var pkb = ""
                                            {% endif %}
                                            Dropzone.autoDiscover = false;
                                            var myDropzone = new Dropzone("div#my-drop-zone", { 
                                                //url: "/uploadedfile/proces/" + pkb,
                                                url: "{% url 'uploadedfile-proces2' pkb %}",
                                                method: "post",
                                                autoProcessQueue: false,
                                                maxFiles: 1,
                                                addRemoveLinks: true,
                                                maxfilesexceeded: function(file) {
                                                    this.removeAllFiles();
                                                    this.addFile(file);
                                                },
                                                init: function () {
                                                    var myDropzone = this;
                                                    var addButton = $("#submit-btn2");
                                                    addButton.click(function (e) {
                                                        
                                                    if (myDropzone.getQueuedFiles().length > 0) {
                                                        
                                                        e.preventDefault();
                                                        myDropzone.processQueue();
                                                        
                                                    }
                                                    });
                                                },
                                                sending: function (file, xhr, formData) {
                                                    formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
                                                    formData.append("image_title", $('#id_image_title').val());
                                                    formData.append('filecategory', $('#id_filecategory').val());
                                                    formData.append('image_contents', $('#id_image_contents').val());

                                                    //setTimeout(function () {
                                                    //        window.location.href='/uploadedfile/show/';
                                                    //}, 1000);

                                                }
                                            });
                                            function getCookie(name) {
                                                var cookieValue = null;
                                                if (document.cookie && document.cookie != '') {
                                                    var cookies = document.cookie.split(';');
                                                    for (var i = 0; i < cookies.length; i++) {
                                                        var cookie = jQuery.trim(cookies[i]);
                                                        // Does this cookie string begin with the name we want?
                                                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                                            break;
                                                        }
                                                    }
                                                }
                                                return cookieValue;
                                            }
                                            $("#my-drop-zone").addClass("dropzone");
                                        </script>
                                        """),

        )

    class Meta:
        model = UploadedFile
        fields = ('image_title', 'filecategory', 'file', 'image_contents',)

class IllustrationLayoutTypeForm(forms.ModelForm):
    '''
        Form to create or edit an illustration layout type. Can add Publications to the to be created illustration layout type object.
        If its a illustration layout type edit load all linked publications.
        If its a illustration layout type create do not load any publications at start.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='btn-danger')))

    class Meta:
        model = IllustrationLayoutType
        fields = ('name',)

    def save(self, commit=True):
        instance = super().save(commit)
        return instance
