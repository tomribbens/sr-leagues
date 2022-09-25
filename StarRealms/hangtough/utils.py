from django.utils import timezone

import hangtough.models as m
import StarRealms.formatgenerator as fg

def get_heat_players(heat):
    players = set()
    for game in heat.game_set.all():
        players.add(game.player1)
        players.add(game.player2)

    return players

def create_heat(track, num_players):
    print("Hitting Util function")
    new_heat = m.Heat(
        current_heat = 1,
        track = track,
        previous_heat = None,
        end_date = None
    )
    new_heat.save()

    new_heat_players = set()
    while num_players:
        new_player = m.Waitlist.objects.filter(track=track).first()
        for existing_player in new_heat_players:
            new_game = m.Game(
                format=eval("fg." + track.formatstrategy).get_format(),
                player1=new_player.player,
                player2=existing_player,
            )
            new_game.save()
            new_game.heat.add(new_heat)
        new_heat_players.add(new_player.player)
        new_player.delete()
        num_players -= 1

    return new_heat

