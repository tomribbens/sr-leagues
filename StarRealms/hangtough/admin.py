from django.contrib import admin
from .models import Track, Heat, Game, Waitlist, Results


# Register your models here.
class TrackAdmin(admin.ModelAdmin):
    fields = ['name', 'priority', 'active']


admin.site.register(Track, TrackAdmin)


class HeatAdmin(admin.ModelAdmin):
    fields = ['track', 'current_heat', 'previous_heat', 'start_date', 'end_date']


admin.site.register(Heat, HeatAdmin)


class GameAdmin(admin.ModelAdmin):
    fields = ['heat', 'format', 'player1', 'player2', 'winner']


admin.site.register(Game, GameAdmin)


class WaitlistAdmin(admin.ModelAdmin):
    fields = ['track', 'player', 'entered_waitlist_on']


admin.site.register(Waitlist, WaitlistAdmin)

class ResultsAdmin(admin.ModelAdmin):
    fields = ['heat', 'player', 'wins', 'losses']

admin.site.register(Results, ResultsAdmin)