# Generated manually for adding stock text configuration fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='stock_in_text',
            field=models.CharField(max_length=100, blank=True, null=True, help_text='Text value meaning item is in stock (e.g., "EN STOCK")'),
        ),
        migrations.AddField(
            model_name='supplier',
            name='stock_out_text',
            field=models.CharField(max_length=100, blank=True, null=True, help_text='Text value meaning item is out of stock (e.g., "AGOTADO")'),
        ),
    ]
