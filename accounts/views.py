import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Supplier
from .forms import SupplierForm

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
	success_url = reverse_lazy('supplier_list')

	def form_valid(self, form):
		form.instance.owner = self.request.user
		response = super().form_valid(form)
		messages.success(self.request, 'Supplier created successfully.')
		logger.info('Supplier created: %s by %s', form.instance.name, self.request.user.username)
		return response
