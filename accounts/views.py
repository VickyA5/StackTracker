import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView, CreateView, View, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Supplier
from .forms import SupplierForm, SupplierUploadForm, SupplierConfigForm
from .services.excel_compare import read_excel_dynamic, normalize_columns, compare_stock

logger = logging.getLogger(__name__)


class WelcomeView(TemplateView):
    template_name = 'welcome.html'


class RegisterView(FormView):
	template_name = 'register.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('home')

	def form_valid(self, form):
		try:
			user = form.save()
			login(self.request, user)
			messages.success(self.request, 'Registration successful. Welcome!')
			logger.info('New user registered: %s', user.username)
			return redirect(self.get_success_url())
		except Exception as exc:
			logger.exception('Error registering user: %s', exc)
			messages.error(self.request, 'An error occurred while creating the user.')
			return self.form_invalid(form)

	def form_invalid(self, form):
		messages.error(self.request, 'Please fix the form errors and try again.')
		return render(self.request, self.template_name, {'form': form})


class DashboardView(LoginRequiredMixin, TemplateView):
	login_url = reverse_lazy('welcome')
	template_name = 'home.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# include only the current user's suppliers for display on home
		context['suppliers'] = Supplier.objects.filter(owner=self.request.user).order_by('-updated_at', '-created_at')
		return context


class SupplierListView(LoginRequiredMixin, ListView):
	model = Supplier
	template_name = 'suppliers/list.html'
	context_object_name = 'suppliers'

	def get_queryset(self):
		return Supplier.objects.filter(owner=self.request.user).order_by('-updated_at', '-created_at')


class SupplierCreateView(LoginRequiredMixin, CreateView):
	model = Supplier
	form_class = SupplierForm
	template_name = 'suppliers/create.html'
	success_url = reverse_lazy('home')

	def form_valid(self, form):
		form.instance.owner = self.request.user
		response = super().form_valid(form)
		# If an initial file was provided during creation, store its original name
		try:
			uploaded = form.cleaned_data.get('current_file')
			if uploaded:
				self.object.last_uploaded_filename = getattr(uploaded, 'name', None) or 'stock.xlsx'
				self.object.save(update_fields=['last_uploaded_filename', 'updated_at'])
				logger.info('Initial file set for supplier %s: %s', self.object.name, self.object.last_uploaded_filename)
		except Exception as exc:
			logger.warning('Failed to record initial file name for %s: %s', self.object.name, exc)
		messages.success(self.request, 'Supplier created successfully.')
		logger.info('Supplier created: %s by %s', form.instance.name, self.request.user.username)
		return response


class SupplierUploadView(LoginRequiredMixin, View):
	template_name = 'suppliers/upload.html'

	def get(self, request, pk):
		supplier = get_object_or_404(Supplier, pk=pk, owner=request.user)
		form = SupplierUploadForm()
		return render(request, self.template_name, {'form': form, 'supplier': supplier})

	def post(self, request, pk):
		supplier = get_object_or_404(Supplier, pk=pk, owner=request.user)
		form = SupplierUploadForm(request.POST, request.FILES)
		if not form.is_valid():
			messages.error(request, 'Please select a valid Excel file.')
			return render(request, self.template_name, {'form': form, 'supplier': supplier})

		upload_file = form.cleaned_data['file']

		# Capture file names for UI
		old_original_name = supplier.last_uploaded_filename
		new_original_name = getattr(upload_file, 'name', 'stock.xlsx')

		# Load previous file (if exists) into memory for comparison
		old_df = None
		if supplier.current_file and supplier.current_file.name:
			try:
				old_df_raw = read_excel_dynamic(supplier.current_file.path, supplier.product_id_column)
				old_df = normalize_columns(
					old_df_raw,
					product_id=supplier.product_id_column,
					stock_col=supplier.stock_column,
					price_col=supplier.price_column,
					name_col=supplier.product_name_column,
					stock_in_text=supplier.stock_in_text,
					stock_out_text=supplier.stock_out_text,
				)
				logger.info('Loaded previous file for supplier %s', supplier.name)
			except Exception as exc:
				logger.warning('Failed to read previous file for %s: %s', supplier.name, exc)

		# Read new upload into memory before saving
		try:
			new_df_raw = read_excel_dynamic(upload_file, supplier.product_id_column)
			new_df = normalize_columns(
				new_df_raw,
				product_id=supplier.product_id_column,
				stock_col=supplier.stock_column,
				price_col=supplier.price_column,
				name_col=supplier.product_name_column,
				stock_in_text=supplier.stock_in_text,
				stock_out_text=supplier.stock_out_text,
			)
		except Exception as exc:
			logger.exception('Error reading uploaded Excel: %s', exc)
			messages.error(request, f'Error reading Excel file: {exc}')
			return render(request, self.template_name, {'form': form, 'supplier': supplier})

		# Compare old vs new
		comparison = compare_stock(old_df, new_df)

		# Overwrite previous file with the new one: delete then save with fixed name
		try:
			if supplier.current_file and supplier.current_file.name:
				supplier.current_file.delete(save=False)
			fixed_name = f"user_{request.user.id}/supplier_{supplier.id}/stock.xlsx"
			supplier.current_file.save(fixed_name, upload_file, save=False)
			supplier.last_uploaded_filename = new_original_name
			supplier.save(update_fields=['current_file', 'last_uploaded_filename', 'updated_at'])
			logger.info('Saved new file for supplier %s (original: %s)', supplier.name, supplier.last_uploaded_filename)
		except Exception as exc:
			logger.exception('Failed to save uploaded file: %s', exc)
			messages.error(request, 'Failed to save uploaded file.')
			return render(request, self.template_name, {'form': form, 'supplier': supplier})

		# Prepare data for UI: convert DataFrames to records for session storage
		def df_records(df):
			try:
				records = df.to_dict('records')
				# Sanitize NaN/None to ensure session JSON serialization and clean UI rendering
				def clean_val(v):
					try:
						# Convert NaN-like to None
						if v is None:
							return None
						sv = str(v).strip().lower()
						if sv in ('nan', '<na>'):
							return None
						return v
					except Exception:
						return None
				return [
					{k: clean_val(v) for k, v in rec.items()}
					for rec in records
				]
			except Exception:
				return []

		request.session['comparison_results'] = {
			'supplier_id': supplier.id,
			'supplier_name': supplier.name,
			'old_file_name': old_original_name,
			'new_file_name': new_original_name,
			'removed_or_out_of_stock': df_records(comparison['removed_or_out_of_stock']),
			'new_products': df_records(comparison['new_products']),
			'stock_changes': df_records(comparison['stock_changes']),
			'price_changes': df_records(comparison['price_changes']),
		}
		messages.success(request, 'File uploaded and comparison completed.')
		return redirect('supplier_comparison', pk=supplier.id)


class ComparisonResultView(LoginRequiredMixin, View):
	template_name = 'suppliers/comparison.html'

	def get(self, request, pk):
		supplier = get_object_or_404(Supplier, pk=pk, owner=request.user)
		data = request.session.get('comparison_results') or {}
		if not data or data.get('supplier_id') != supplier.id:
			messages.info(request, 'No comparison data available for this supplier. Please upload a file.')
			return redirect('supplier_upload', pk=supplier.id)

		context = {
			'supplier': supplier,
			'old_file_name': data.get('old_file_name'),
			'new_file_name': data.get('new_file_name'),
			'removed_or_out_of_stock': data.get('removed_or_out_of_stock', []),
			'new_products': data.get('new_products', []),
			'stock_changes': data.get('stock_changes', []),
			'price_changes': data.get('price_changes', []),
		}
		return render(request, self.template_name, context)


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
	model = Supplier
	template_name = 'suppliers/delete.html'
	success_url = reverse_lazy('home')

	def get_queryset(self):
		return Supplier.objects.filter(owner=self.request.user)

	def delete(self, request, *args, **kwargs):
		obj = self.get_object()
		name = obj.name
		try:
			if obj.current_file:
				obj.current_file.delete(save=False)
		except Exception as exc:
			logger.warning('Failed to delete file for supplier %s: %s', name, exc)
		logger.info('Supplier deleted: %s by %s', name, request.user.username)
		messages.success(request, f'Supplier "{name}" deleted successfully.')
		return super().delete(request, *args, **kwargs)


class SupplierSettingsView(LoginRequiredMixin, CreateView):
	model = Supplier
	form_class = SupplierConfigForm
	template_name = 'suppliers/settings.html'
	success_url = reverse_lazy('home')

	def dispatch(self, request, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)

	def get_object(self, queryset=None):
		return get_object_or_404(Supplier, pk=self.kwargs['pk'], owner=self.request.user)

	def get(self, request, *args, **kwargs):
		supplier = self.get_object()
		form = self.form_class(instance=supplier)
		return render(request, self.template_name, {'form': form, 'supplier': supplier})

	def post(self, request, *args, **kwargs):
		supplier = self.get_object()
		form = self.form_class(request.POST, instance=supplier)
		if form.is_valid():
			form.save()
			messages.success(request, 'Supplier columns updated successfully.')
			logger.info('Supplier columns updated for %s by %s', supplier.name, request.user.username)
			return redirect(self.success_url)
		messages.error(request, 'Please fix the form errors and try again.')
		return render(request, self.template_name, {'form': form, 'supplier': supplier})
