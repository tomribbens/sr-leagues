from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .utils import get_heat_players


# Create your models here.
class Track(models.Model):
    name = models.TextField(max_length=50)
    priority = models.IntegerField(unique=True)
    active = models.BooleanField()
    formatstrategy = models.TextField(max_length=50, default="Vanilla")

    def __str__(self):
        return self.name + ":" + str(self.priority)

    class Meta:
        ordering = ['priority']


class Heat(models.Model):
    current_heat = models.IntegerField()
    track = models.ForeignKey(Track, on_delete=models.PROTECT)
    previous_heat = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField('Start Date', default=timezone.now)
    end_date = models.DateTimeField('End Date', null=True, blank=True)

    def __str__(self):
        return str(self.track.id) + ":" + str(self.previous_heat) + ":" + str(self.start_date) + ":" + str(self.end_date)

    def get_all_players(self):
        players = {}

        return players

    def get_standings(self):
        players = self.get_all_players()


    class Meta:
        unique_together = ('track', 'current_heat')


class Results(models.Model):
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.PROTECT)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return self.player.username + ": " + str(self.wins) + "/" + str(self.losses)

    class Meta:
        ordering = ['-wins', 'losses']


class Game(models.Model):
    heat = models.ManyToManyField(Heat)
    format = models.TextField(max_length=20, default="V")
    player1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name='player1')
    player2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name='player2')
    winner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='winner', null=True, blank=True)

    def __str__(self):
        return self.player1.username + " vs " + self.player2.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        for heat in self.heat.all():
            players = get_heat_players(heat)

            for player in players:
                result, created = Results.objects.get_or_create(heat=heat, player=player)
                result.wins = heat.game_set.filter(winner=player).count()
                result.losses = heat.game_set.filter(models.Q(player1 = player) | models.Q(player2 = player), ~models.Q(winner = player), winner__isnull = False).count()
                result.save()


class Waitlist(models.Model):
    track = models.ForeignKey(Track, on_delete=models.PROTECT)
    entered_waitlist_on = models.DateTimeField('Entered Waitlist', default=timezone.now)
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.track.name) + ": " + self.player.username

    class Meta:
        unique_together = ('track', 'player')
        ordering = ['entered_waitlist_on']

class Log(models.Model):
    timestamp = models.DateTimeField('Timestamp', auto_now=True)
    message = models.TextField(max_length=255)
