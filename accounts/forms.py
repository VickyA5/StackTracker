from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'product_id_column', 'stock_column', 'price_column', 'stock_in_text', 'stock_out_text', 'current_file']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Supplier name'}),
            'product_id_column': forms.TextInput(attrs={'placeholder': 'e.g. sku or product_id'}),
            'stock_column': forms.TextInput(attrs={'placeholder': 'e.g. stock_qty'}),
            'price_column': forms.TextInput(attrs={'placeholder': 'e.g. price (optional)'}),
            'stock_in_text': forms.TextInput(attrs={'placeholder': 'e.g. EN STOCK (optional)'}),
            'stock_out_text': forms.TextInput(attrs={'placeholder': 'e.g. AGOTADO (optional)'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()


class SupplierUploadForm(forms.Form):
    file = forms.FileField(allow_empty_file=False)

    def clean_file(self):
        f = self.cleaned_data['file']
        # Basic check for Excel extension
        name = (getattr(f, 'name', '') or '').lower()
        if not (name.endswith('.xlsx') or name.endswith('.xls')):
            raise forms.ValidationError('Please upload an Excel file (.xlsx or .xls).')
        return f
