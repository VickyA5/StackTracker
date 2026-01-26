from django.conf import settings
from django.db import models
import os



def supplier_upload_path(instance: "Supplier", filename: str) -> str:
    user_id = instance.owner_id or (instance.owner and instance.owner.id) or 'unknown'
    supplier_id = instance.id or 'unknown'
    # Always use a fixed filename so last upload overwrites
    return os.path.join(f"user_{user_id}", f"supplier_{supplier_id}", "stock.xlsx")


class Supplier(models.Model):
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suppliers'
	)
	name = models.CharField(max_length=200)
	product_id_column = models.CharField(max_length=100, help_text='Column name that contains the product identifier')
	stock_column = models.CharField(max_length=100, help_text='Column name that contains stock quantities')
	price_column = models.CharField(max_length=100, blank=True, null=True, help_text='Column name that contains price (optional)')
	# Optional text values for stock when the column is non-numeric
	stock_in_text = models.CharField(max_length=100, blank=True, null=True, help_text='Text value meaning item is in stock (e.g., "EN STOCK")')
	stock_out_text = models.CharField(max_length=100, blank=True, null=True, help_text='Text value meaning item is out of stock (e.g., "AGOTADO")')
	last_uploaded_filename = models.CharField(max_length=255, blank=True, null=True, help_text='Original name of the last uploaded file')
	current_file = models.FileField(upload_to=supplier_upload_path, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-updated_at']

	def __str__(self) -> str:
		return f"{self.name} ({self.owner})"
