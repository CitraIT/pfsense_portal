from django import forms
from .models import Firewall
#from customer.models import Customer


class FirewallForm(forms.ModelForm):
    required_css_class = 'required'
    
    class Meta:
        model = Firewall
        fields = '__all__'
        labels = {
            'name': 'Nome',
            'api_key': 'API Key',
        }
    
