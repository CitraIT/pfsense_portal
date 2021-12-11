from django import forms
from .models import Firewall


class FirewallForm(forms.ModelForm):
    required_css_class = 'required'
    
    class Meta:
        model = Firewall
        fields = '__all__'
        labels = {
            'name': 'Nome',
            'url': 'URL',
            'admin_user': 'Admin User',
            'admin_pass': 'Admin Password'
        }
    
