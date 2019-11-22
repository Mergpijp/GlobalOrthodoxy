from django import forms

from .models import Publication

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class PublicationForm(forms.ModelForm):
    
    class Meta:
        model = Publication
        fields = ('title_original', 'title_subtitle_transcription', 'title_subtitle_european', 'title_translation', 'author', 'translator', )
    def __init__(self, *args, **kwargs):
        super(PublicationForm, self).__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['translator'].required = False
        

   