from django import forms

from .models import Publication, Author, Translator, FormOfPublication, Genre, Church, SpecialOccasion, Owner, City, Language, Country, IllustrationLayoutType, UploadedFile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Field
from crispy_forms.bootstrap import Tab, TabHolder, FieldWithButtons, StrictButton
from django.forms.models import inlineformset_factory
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget, ModelSelect2TagWidget, Select2Widget, ModelSelect2Widget, HeavySelect2MultipleWidget
from django_countries.fields import CountryField
from django_countries import countries
from django_countries.widgets import CountrySelectWidget



class CustomCountrySelectWidget(Select2Widget, CountrySelectWidget):
    pass

class AuthorWdiget(ModelSelect2MultipleWidget):
    model = Author
    search_fields = ['firstname__icontains', 'lastname__icontains']

    def label_from_instance(self,obj):
        return obj.name

    def get_queryset(self):
        return Author.objects.all()
        
    def filter_queryset(self, queryset=None):
        return queryset.filter(do='whaterver')
        
    def get_model_field_values(self, value):
        return {'title': value}

    def prepare_qs_params(self, request, search_term, search_fields):
        res = super(Endpoints, self).prepare_qs_params(request, search_term, search_fields)
        res['and'] = {'id': request.GET.get('id')}
        return res

class PublicationForm(forms.ModelForm):
    author = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Author,
        search_fields=['firstname__icontains', 'lastname__icontains'],
    ), queryset=Author.objects.all(), required=False)
    translator = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Translator,
        search_fields=['firstname__icontains', 'lastname__icontains'],
    ), queryset=Translator.objects.all(), required=False)
    form_of_publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=FormOfPublication,
        search_fields=['name__icontains',],
    ), queryset=FormOfPublication.objects.all(), required=False)
    publication_city = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=City,
        search_fields=['name__icontains',],
    ), queryset=City.objects.all(), required=False)    
    affiliated_church = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Church,
        search_fields=['name__icontains',],
    ), queryset=Church.objects.all(), required=False)
    language = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Language,
        search_fields=['name__icontains',],
    ), queryset=Language.objects.all(), required=False)    
    content_genre = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Genre,
        search_fields=['name__icontains',],
    ), queryset=Genre.objects.all(), required=False)        
    connected_to_special_occasion = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=SpecialOccasion,
        search_fields=['name__icontains',],
    ), queryset=SpecialOccasion.objects.all(), required=False)   
    currently_owned_by = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Owner,
        search_fields=['name__icontains',],
    ), queryset=Owner.objects.all(), required=False) 
    uploadedfiles = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=UploadedFile,
        search_fields=['description__icontains',],
    ), queryset=UploadedFile.objects.all(), required=False) 
    class Meta:
        model = Publication
        fields = ('title_original', 'title_subtitle_transcription', 'title_subtitle_European', 'title_translation', 'author', 'translator', \
                  'form_of_publication', 'printed_by', 'published_by', 'publication_date', 'publication_country', 'publication_city', 'publishing_organisation', \
                  'possible_donor', 'affiliated_church', 'language', 'content_description', 'content_genre', 'connected_to_special_occasion', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights', 'currently_owned_by', 'contact_telephone_number', \
                  'contact_email', 'contact_website','comments', 'uploadedfiles')
        
    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['translator'].required = False
        self.fields['affiliated_church'].required = False
        self.fields['language'].required = False
        self.fields['content_genre'].required = False
        self.fields['connected_to_special_occasion'].required = False
        self.fields['currently_owned_by'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['uploadedfiles'].required = False
      
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'  
       
        self.helper.layout = Layout(
            TabHolder(
                Tab('Titles',
                'title_original',
                'title_subtitle_transcription',
                'title_subtitle_European',
                'title_translation',
                
                ),
                Tab('Author',
                    'author',
                    'translator',
                ),
                Tab('Publishing information',
                    'form_of_publication',
                    'printed_by',
                    'published_by',
                    'publication_date',
                    'publication_country',
                    'publication_city',
                    'publishing_organisation',
               ),
               Tab('Affiliation',
                   'possible_donor',
                   'affiliated_church',
              ),
               Tab('Language',
                   'language',
              ),
               Tab('Content',
                   'content_description',
                   'content_genre',
                   'connected_to_special_occasion',
                   'description_of_illustration',
                   'image_details',
                   'nr_of_pages',
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
                   'comments',
             ),
              Tab('Files',
                  'uploadedfiles',
                 )
            ),
            ButtonHolder(
                Submit('search', 'Search', css_class='button white')
            )
        )

class NewCrispyForm(forms.ModelForm):
    author = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Author,
        search_fields=['firstname__icontains', 'lastname__icontains'],
    ), queryset=Author.objects.all(), required=False)
    translator = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Translator,
        search_fields=['firstname__icontains', 'lastname__icontains'],
    ), queryset=Translator.objects.all(), required=False)
    form_of_publication = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=FormOfPublication,
        search_fields=['name__icontains',],
    ), queryset=FormOfPublication.objects.all(), required=False)
    publication_city = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=City,
        search_fields=['name__icontains',],
    ), queryset=City.objects.all(), required=False)    
    affiliated_church = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Church,
        search_fields=['name__icontains',],
    ), queryset=Church.objects.all(), required=False)
    language = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Language,
        search_fields=['name__icontains',],
    ), queryset=Language.objects.all(), required=False)    
    content_genre = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Genre,
        search_fields=['name__icontains',],
    ), queryset=Genre.objects.all(), required=False)        
    connected_to_special_occasion = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=SpecialOccasion,
        search_fields=['name__icontains',],
    ), queryset=SpecialOccasion.objects.all(), required=False)   
    currently_owned_by = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Owner,
        search_fields=['name__icontains',],
    ), queryset=Owner.objects.all(), required=False) 
    uploadedfiles = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=UploadedFile,
        search_fields=['description__icontains',],
    ), queryset=UploadedFile.objects.all(), required=False)    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        #self.helper.form_id = 'id-my-form'
        #self.helper.form_class = 'my-form'
        #self.helper.form_method = 'post'
        self.fields['author'].required = False
        self.fields['translator'].required = False
        self.fields['affiliated_church'].required = False
        self.fields['language'].required = False
        self.fields['content_genre'].required = False
        self.fields['connected_to_special_occasion'].required = False
        self.fields['currently_owned_by'].required = False
        self.fields['form_of_publication'].required = False
        self.fields['uploadedfiles'].required = False
        self.helper.layout = Layout(
            TabHolder(
                Tab('Titles',
                'title_original',
                'title_subtitle_transcription',
                'title_subtitle_European',
                'title_translation',
                ),
                Tab('Author',
                    FieldWithButtons('author', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/author/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    FieldWithButtons('translator', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/translator/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                ),
                Tab('Publishing information',
                    FieldWithButtons('form_of_publication', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/form_of_publication/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'printed_by',
                    'published_by',
                    'publication_date',
                    'publication_country',
                    FieldWithButtons('publication_city', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/city/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                    'publishing_organisation',
               ),
               Tab('Affiliation',
                   'possible_donor',
                   FieldWithButtons('affiliated_church', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/church/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
              ),
               Tab('Language',
                   FieldWithButtons('language', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/language/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
              ),
               Tab('Content',
                   'content_description',
                   FieldWithButtons('content_genre', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/genre/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                   FieldWithButtons('connected_to_special_occasion', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/special_occasion/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                   'description_of_illustration',
                   'image_details',
                   'nr_of_pages',
              ),
               Tab('Collection info',
                   'collection_date',
                   'collection_country',
                   'collection_venue_and_city',
                   'copyrights',
                   FieldWithButtons('currently_owned_by', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/owner/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                   'contact_telephone_number',
                   'contact_email',
                   'contact_website',
                   'comments',
             ),
              Tab('Files',
                  FieldWithButtons('uploadedfiles', StrictButton('+', type='button', css_class='btn-primary', onClick="window.open('/uploadedfile/new', '_blank', 'width=1000,height=600,menubar=no,toolbar=no');")),
                 )
            ),
            ButtonHolder(
                Submit('Submit', 'Submit', css_class='button white')
            )
        )

    class Meta:
        model = Publication
        # See note here: https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
        fields = ('title_original', 'title_subtitle_transcription', 'title_subtitle_European', 'title_translation', 'author', 'translator', \
                  'form_of_publication', 'printed_by', 'published_by', 'publication_date', 'publication_country', 'publication_city', 'publishing_organisation', \
                  'possible_donor', 'affiliated_church', 'language', 'content_description', 'content_genre', 'connected_to_special_occasion', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights', 'currently_owned_by', 'contact_telephone_number', \
                  'contact_email', 'contact_website','comments', 'uploadedfiles')
        #publication_country = forms.ChoiceField(choices=list(countries))
  
class AuthorForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        model=Publication,
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(author=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('firstname', 'lastname', 'year_of_birth', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Author
        fields = ('firstname', 'lastname', 'year_of_birth')
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
        return instance        

class TranslatorForm(forms.ModelForm):

    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(translator=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('firstname', 'lastname', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Translator
        fields = ('firstname', 'lastname') 
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
        return instance  

class FormOfPublicationForm(forms.ModelForm):

    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(form_of_publication=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = FormOfPublication
        fields = ('name',) 
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
        return instance         
        
class CityForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(publication_city=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'country', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = City
        fields = ('name','country',) 
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance         
          
        
class ChurchForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(affiliated_church=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Church
        fields = ('name',)  
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance 
        

class LanguageForm(forms.ModelForm):
    #publications = forms.MultipleChoiceField(queryset=Publication.objects.all(), widget=Select2MultipleWidget)
    #ModelSelect2MultipleWidget
    #initial_values = Publication.objects.filter(language=self.instance)
    #publications = forms.ModelMultipleChoiceField(queryset=Publication.objects.all(), required=False)
   
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(language=self.instance)
        
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'direction', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Language
        fields = ('name', 'direction',)
        
        
    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance        
   
class GenreForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(content_genre=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Genre
        fields = ('name',) 
        
    def save(self, commit=True):
        instance = super().save(commit)

        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance  

class SpecialOccasionForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(connected_to_special_occasion=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = SpecialOccasion
        fields = ('name',) 
        
    def save(self, commit=True):
        instance = super().save(commit)

        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance 

class OwnerForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(currently_owned_by=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Owner
        fields = ('name',) 
        
    def save(self, commit=True):
        instance = super().save(commit)

        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance 

class UploadedFileForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(uploadedfiles=self.instance)
        self.helper = FormHelper()
        self.helper.layout = Layout('description', 'files', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = UploadedFile
        fields = ('description', 'files',) 
        
    def save(self, commit=True):
        instance = super().save(commit)

        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance 
        

class IllustrationLayoutTypeForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains', 'title_original__icontains', 'title_subtitle_transcription__icontains', 'title_translation__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['publications'].initial = Publication.objects.filter(illustration_and_layout_type=self.instance)        
        self.helper = FormHelper()
        self.helper.layout = Layout('name', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = IllustrationLayoutType
        fields = ('name',) 
        
    def save(self, commit=True):
        instance = super().save(commit)

        if self.cleaned_data['publications'].count() > instance.publication_set.count():
            diff = set(self.cleaned_data['publications'].all()) - set(instance.publication_set.all()) 
            for pub in diff:
                instance.publication_set.add(pub)
        
        elif self.cleaned_data['publications'].count() < instance.publication_set.count():
            diff = set(instance.publication_set.all()) - set(self.cleaned_data['publications'].all()) 
            if not diff:
                for pub in instance.publication_set:
                    instance.publication_set.remove(pub)
            for pub in diff:
               instance.publication_set.remove(pub)
               
        return instance             