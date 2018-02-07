from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from models import Game, Coin


class GameManager:

    @staticmethod
    def get_current_games(user):
        """

        :return:
        """
        return Game.objects.filter(
            ~Q(status=Game.Status.finished),
            Q(player1=user) | Q(player2=user)
        )

    @staticmethod
    def get_join_up_games(user):
        """

        :return:
        """
        return Game.objects.filter(
            ~Q(status=Game.Status.finished),
            ~Q(player1=user) & Q(player2__isnull=True)
        )

    @staticmethod
    def get_concluded_games(user):
        return Game.objects.filter(
            Q(status=Game.Status.finished),
            Q(player1=user) | Q(player2=user)
        )

    @staticmethod
    def create_new_game(user):
        return Game.objects.create(
            player1=user,
            status=Game.Status.new,
        )
