import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
	template_name = 'home.html'


class RegisterView(FormView):
	template_name = 'register.html'
	form_class = UserCreationForm
	success_url = '/'

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
