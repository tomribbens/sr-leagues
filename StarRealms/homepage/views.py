from django.views.generic.base import TemplateView
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .forms import NewUserForm
from hangtough.models import Game

class HomePageView(TemplateView):
    template_name = 'homepage/index.html'

class RegisterView(TemplateView):
    template_name = 'homepage/register.html'

    def get_context_data(self, **kwargs):
        context = {}
        form = NewUserForm()
        context["register_form"] = form
        return context


    def post(self, request, **kwargs):
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccesful registration. Invalid information.")

        context = self.get_context_data(**kwargs)
        self.render_to_response(context)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'homepage/profile.html'

    def get_context_data(self, **kwargs):
        context = dict()
        user = self.request.user
        open_games = Game.objects.filter(Q(player1=user) | Q(player2=user), winner__isnull=True)
        context['open_games'] = open_games
        return context
