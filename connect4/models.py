from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from djchoices import DjangoChoices, ChoiceItem

# Create your models here.
CONNECT4_SIZE = 6


@python_2_unicode_compatible
class Game(models.Model):

    class Status(DjangoChoices):
        """Enum class for the different possible status of a game."""
        new = ChoiceItem('new')
        first_player = ChoiceItem('player1')
        second_player = ChoiceItem('player2')
        finished = ChoiceItem('finished')

    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_1')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_2', blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices)
    winner = models.CharField(max_length=10)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.player2:
            return ' vs '.join([self.player1.get_full_name(), self.player2.get_full_name()])

        else:
            return 'Join now to play %s' % self.player1.get_short_name()

    @property
    def start_date(self):
        return self.coin_set.order_by('created_date')[0].created_date

    @property
    def last_move(self):
        return self.coin_set.order_by('-created_date')[0]

    @property
    def last_action_date(self):
        return self.last_move.created_date

    def join_up(self, player_2):
        if self.player2 is None:
            self.player2 = player_2
            self.save()
            return True
        else:
            return False

    def create_new_coin(self, user):
        return Coin(game=self, player=user)

    def player_context(self, user):
        player = None
        if self.player1 == user:
            player = Game.Status.first_player
        elif self.player2 == user:
            player = Game.Status.second_player
        next_turn = self.status == player
        return player, next_turn

    def get_play_url(self):
        return reverse('play_game', args=[self.id])

    def is_pending(self):
        return not (self.status == Game.Status.new or self.status == Game.Status.finished)

    def is_valid_location(self, row, column):
        return not self.coin_set.filter(row=row, column=column).exists() and \
               (self.coin_set.filter(row=row-1, column=column).exists() or row == 0)

    def update_game(self, coin, user):
        coin.player = user
        coin.save()
        game_over = self.calculate_status(user)
        player, _ = self.player_context(user)
        if game_over is None:
            # Draw
            self.status = Game.Status.finished
        elif game_over:
            # Win
            self.status = Game.Status.finished
            self.winner = player
        else:
            # Toggle
            self.status = Game.Status.first_player if player == Game.Status.second_player else Game.Status.second_player
        self.save()
        return self.status == Game.Status.finished

    def calculate_status(self, user):
        count_all = Coin.objects.count()

        for coin in Coin.objects.filter(player=user).order_by('row', 'column'):
            if coin.column + 3 <= CONNECT4_SIZE and coin.row + 3 <= CONNECT4_SIZE:
                for i in range(4):
                    if not Coin.objects.filter(player=user, row=coin.row+i, column=coin.column+i).exists():
                        break
                else:
                    return True
            elif count_all == CONNECT4_SIZE ** 2:
                # Draw condition
                return None
            else:
                return False

            if coin.row + 3 <= CONNECT4_SIZE:
                if Coin.objects.filter(
                        player=user,
                        row__gte=coin.row,
                        row__lte=coin.row + 3,
                        column=coin.column
                ).count() == 4:
                    return True
            if coin.column + 3 <= CONNECT4_SIZE:
                if Coin.objects.filter(
                    player=user,
                    row=coin.row,
                    column__gte=coin.row,
                    column__lte=coin.row + 3
                ).count() == 4:
                    return True

        return False


@python_2_unicode_compatible
class Coin(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    column = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(CONNECT4_SIZE - 1)])
    row = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(CONNECT4_SIZE - 1)])
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return ' '.join([
            self.player, 'to', self.row, self.column
        ])

