from django.utils import timezone
from django.db import IntegrityError
from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.http import HttpResponse

import StarRealms.formatgenerator as fg
from .models import Heat, Waitlist, Track, Game, Results
from .utils import get_heat_players, create_heat


class HomePageView(ListView):
    model = Heat

    def get_queryset(self):
        return Heat.objects.filter(end_date__isnull = True)


    template_name = 'hangtough/index.html'

class RemoveFromWaitlistView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.is_staff and request.user.pk != kwargs['id']:
            raise PermissionDenied

        Waitlist.objects.filter(track__id=kwargs['track'], player__id=kwargs['player_id']).delete()
        return redirect('hangtough:index')

class JoinWaitlistView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not request.user.is_staff and request.user.pk != kwargs['player_id']:
            raise PermissionDenied

        player = User.objects.get(pk=kwargs['player_id'])

        if any(player in (game.player1, game.player2) for game in Game.objects.filter(heat__track__id=kwargs['track'], heat__end_date__isnull=True)):
            return redirect('hangtough:index')

        try:
            w = Waitlist(track=Track.objects.get(pk=kwargs['track']), player=player)
            w.save()
        except IntegrityError:
            return redirect('hangtough:index')


        return redirect('hangtough:index')

class RecordWinView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        game = Game.objects.get(pk=kwargs['game_id'])

        if not request.user.is_staff and request.user not in (game.player1, game.player2):
            raise PermissionDenied

        if game.winner:
            return redirect('hangtough:index')

        game.winner = User.objects.get(pk=kwargs['player_id'])
        game.save()

        return redirect('hangtough:index')


class HangtoughAdmin(UserPassesTestMixin, TemplateView):
    template_name = "hangtough/admin.html"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = dict()
        context['tracks'] = Track.objects.all()
        if not hasattr(self, 'track') or not self.track:
            return context

        context['track'] = self.track

        try:
            heat = Heat.objects.get(track = self.track, end_date__isnull = True)
        except Heat.DoesNotExist:
            if not hasattr(self, 'new_track') or not self.new_track:
                context['actions'] = ['create_from_scratch']
                return context

            if self.new_track > Waitlist.objects.filter(track=self.track).count():
                raise Exception

            heat = create_heat(self.track, self.new_track)

        all_games_done = not bool(heat.game_set.filter(winner__isnull = True).count())
        if not all_games_done:
            context['message'] = "Not all games are done in this Heat"
            return context

        if not hasattr(self, 'finish_heat') or not self.finish_heat:
            context['heat'] = heat
            context['actions'] = ['finish_heat']
            return context

        heat.end_date = timezone.now()
        heat.save()

        new_heat = Heat(
            current_heat=heat.current_heat + 1,
            track = self.track,
            previous_heat = heat,
            start_date = timezone.now(),
            end_date = None,
        )
        new_heat.save()

        players = get_heat_players(heat)
        to_remove = set()
        for player in players:
            player_wins = Results.objects.get(heat=heat, player=player).wins
            if player_wins <= self.finish_heat:
                to_remove.add(player)

        num_removed_players = len(to_remove)
        new_heat_players = players.difference(to_remove)

        for game in heat.game_set.all():
            if game.player1 in new_heat_players and game.player2 in new_heat_players:
                game.heat.add(new_heat)

        if num_removed_players > Waitlist.objects.filter(track=self.track).count():
            raise Exception

        while num_removed_players:
            new_player = Waitlist.objects.filter(track=self.track).first()
            for existing_player in new_heat_players:
                new_game = Game(
                    format=eval("fg." + self.track.formatstrategy).get_format(),
                    player1=new_player.player,
                    player2=existing_player,
                )
                new_game.save()
                new_game.heat.add(new_heat)
            new_heat_players.add(new_player.player)
            new_player.delete()
            num_removed_players -= 1

        context['message'] = "New heat created"
        return context

    def post(self, request, *args, **kwargs):
        track_id = request.POST.get('track_id', False)
        if track_id:
            self.track = Track.objects.get(pk=track_id)

        new_track = request.POST.get('new_track', False)
        if new_track:
            self.new_track = int(new_track)

        finish_heat = request.POST.get('finish_heat', False)
        if finish_heat:
            self.finish_heat = int(finish_heat)

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
