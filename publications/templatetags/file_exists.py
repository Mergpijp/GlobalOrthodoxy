from django import template
from django.core.files.storage import default_storage

register = template.Library()
import pdb

@register.filter(name='file_exists')
def file_exists(filepath):
    #pdb.set_trace()
    if default_storage.exists(filepath):
        return filepath
    else:
        #pdb.set_trace()
        return 'f9b221362b1527ef018dd75b4cbd92d7'