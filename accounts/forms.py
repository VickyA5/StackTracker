from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'product_id_column', 'stock_column', 'price_column', 'current_file']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Supplier name'}),
            'product_id_column': forms.TextInput(attrs={'placeholder': 'e.g. sku or product_id'}),
            'stock_column': forms.TextInput(attrs={'placeholder': 'e.g. stock_qty'}),
            'price_column': forms.TextInput(attrs={'placeholder': 'e.g. price (optional)'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()
