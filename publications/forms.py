from django import forms

from .models import Publication, FormOfPublication
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, TabHolder

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class PublicationForm(forms.ModelForm):
    
    #form_of_publication = forms.CharField(max_length=1, choices=[(tag.value, tag) for tag in FormOfPublication], default='O')
    class Meta:
        model = Publication
        fields = ('title_original', 'title_subtitle_transcription', 'title_subtitle_european', 'title_translation', 'author', 'translator', \
                  'form_of_publication', 'printed_by', 'published_by', 'publication_date', 'publication_country', 'publication_city', 'publishing_organisation', \
                  'possible_donor', 'affiliated_church', 'language', 'content_description', 'content_genre', 'connected_to_special_occasion', 'description_of_illustration', \
                  'image_details', 'nr_of_pages', 'collection_date', 'collection_country', 'collection_venue_and_city', 'copyrights', 'currently_owned_by', 'contact_info', \
                  'comments')
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
        `
        '''
        self.helper = FormHelper()
        
       
        self.helper.tabholder = TabHolder(
                Tab('First Tab',
                'field_name_1',
                Div('field_name_2')
            ),
            Tab('Second Tab',
                Field('field_name_3', css_class="extra")
            )
        )
        '''
        #for key in self.fields.keys():
        #    print(self.fields[key].__class__.__name__)
        #    if self.fields[key].__class__.__name__ == 'ModelMultipleChoiceField':
        #        self.fields[key].required = False
        

   