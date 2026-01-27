# Generated manually to add product_name_column to Supplier
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_supplier_last_uploaded_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='product_name_column',
            field=models.CharField(max_length=100, blank=True, null=True, help_text='Optional column name that contains the product name/description'),
        ),
    ]
