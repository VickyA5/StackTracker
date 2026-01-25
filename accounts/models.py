from django.db import models

from django.conf import settings
from django.db import models


class Supplier(models.Model):
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suppliers'
	)
	name = models.CharField(max_length=200)
	product_id_column = models.CharField(max_length=100, help_text='Column name that contains the product identifier')
	stock_column = models.CharField(max_length=100, help_text='Column name that contains stock quantities')
	price_column = models.CharField(max_length=100, blank=True, null=True, help_text='Column name that contains price (optional)')
	current_file = models.FileField(upload_to='supplier_files/', null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-updated_at']

	def __str__(self) -> str:
		return f"{self.name} ({self.owner})"
