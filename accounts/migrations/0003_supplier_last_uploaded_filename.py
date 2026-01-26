# Generated manually for adding last uploaded filename
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_supplier_stock_text_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='last_uploaded_filename',
            field=models.CharField(max_length=255, blank=True, null=True, help_text='Original name of the last uploaded file'),
        ),
    ]