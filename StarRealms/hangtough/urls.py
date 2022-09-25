from django.urls import path

from .views import HomePageView, RemoveFromWaitlistView, JoinWaitlistView, RecordWinView, HangtoughAdmin

app_name = 'hangtough'
urlpatterns = [
    path('', HomePageView.as_view(), name='index'),
    path('removewaitlist/track/<int:track>/player/<int:player_id>', RemoveFromWaitlistView.as_view(), name='removewaitlist' ),
    path('joinwaitlist/track/<int:track>/player/<int:player_id>', JoinWaitlistView.as_view(), name='joinwaitlist'),
    path('recordwin/game/<int:game_id>/player/<int:player_id>', RecordWinView.as_view(), name='recordwin'),
    path('admin', HangtoughAdmin.as_view(), name='admin'),
]