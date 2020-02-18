from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from sheori.register_form import RegisterForm

class RegisterView(CreateView):
    template_name = 'registration/register_form.html'
    form_class = RegisterForm
    success_url = reverse_lazy('register_done')

register_view = RegisterView.as_view()

class DoneView(TemplateView):
    template_name = 'registration/register_done.html'

done_view = DoneView.as_view()