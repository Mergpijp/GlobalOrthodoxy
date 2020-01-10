from django import forms

from .models import Publication, Author, Translator, Genre, Church, SpecialOccasion, Owner, City, Language, Country, IllustrationLayoutType, Document
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Field
from crispy_forms.bootstrap import Tab, TabHolder
from django.forms.models import inlineformset_factory
from django_select2.forms import ModelSelect2MultipleWidget, Select2MultipleWidget, ModelSelect2TagWidget, Select2Widget, ModelSelect2Widget, HeavySelect2MultipleWidget
from django_countries.fields import CountryField
from django_countries import countries

class PublicationForm(forms.ModelForm):
    #need a dummy field for select2 workaround
    something = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Author.objects.all(),
        search_fields=['firstname', 'lastname'],
    ), queryset=Author.objects.all(), required=False)
    
    class Meta:
        model = Publication
        fields = ('title_original', 'title_subtitle_transcription', 'title_subtitle_European', 'title_translation', 'author', 'translator', \
                  'form_of_publication', 'printed_by', 'published_by', 'publication_date', 'publication_country', 'publication_city', 'publishing_organisation', \
                  'possible_donor', 'affiliated_church', 'language', 'content_description', 'content_genre', 'connected_to_special_occasion', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights', 'currently_owned_by', 'contact_info', \
                  'comments', 'documents')
        
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
        self.fields['documents'].required = False
      
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
                   'contact_info',
                   'comments',
             ),
              Tab('Files',
                  'documents',
                 )
            ),
            ButtonHolder(
                Submit('search', 'Search', css_class='button white')
            )
        )
        
class NewCrispyForm(forms.ModelForm):
    #need a dummy field for select2 workaround
    something = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Author.objects.all(),
        search_fields=['firstname', 'lastname'],
    ), queryset=Author.objects.all(), required=False)
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
        self.fields['documents'].required = False
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
                   'contact_info',
                   'comments',
             ),
               Tab('files',
                   'documents',
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
          'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights', 'currently_owned_by', 'contact_info', \
          'comments', 'documents')
        #publication_country = forms.ChoiceField(choices=list(countries))
          
class AuthorForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(author = self.instance)]
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(translator = self.instance)]
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
        
class CityForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(publication_city = self.instance)]
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(affiliated_church = self.instance)]
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(language = self.instance)]
        
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(content_genre = self.instance)]
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(connected_to_special_occasion = self.instance)]
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(currently_owned_by = self.instance)]
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

class DocumentForm(forms.ModelForm):
    publications = forms.ModelMultipleChoiceField(widget=ModelSelect2MultipleWidget(
        queryset=Publication.objects.all(),
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(documents = self.instance)]
        self.helper = FormHelper()
        self.helper.layout = Layout('description', 'document', 'publications',
                                    ButtonHolder(Submit('Submit', 'Submit', css_class='button white') ))
    
    class Meta:
        model = Document
        fields = ('description', 'document',) 
        
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
        search_fields=['title_subtitle_European__icontains'],
    ), queryset=Publication.objects.all(), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['publications'].initial = [pub for pub in Publication.objects.filter(illustration_and_layout_type = self.instance)]
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