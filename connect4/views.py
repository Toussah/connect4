
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from forms import NextMoveForm
from models import Game, CONNECT4_SIZE
from utils import GameManager


# Create your views here.
def login(request):
    """
    Write your login view here
    :param request:
    :return:
    """
    username = request.POST['username']
    password = request.POST['password']
    user = auth.authenticate(request=request, username=username, password=password)
    if user is not None:
        auth.login(request, user)
        return redirect('games/')
    else:
        raise PermissionDenied('Could not identify user.')


def logout(request):
    """
    write your logout view here
    :param request:
    :return:
    """
    auth.logout(request)


def signup(request):
    """
    write your user sign up view here
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(username=username, password=raw_password)
            auth.login(request, user)
            return redirect('games/')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required()
def games(request):
    """
    Write your view which controls the game set up and selection screen here
    :param request:
    :return:
    """
    current_games = GameManager.get_current_games(request.user)
    join_up_games = GameManager.get_join_up_games(request.user)
    concluded_games = GameManager.get_concluded_games(request.user)
    return render(
        request, 'play/game_display_all.html',
        {
            'current_games': current_games,
            'join_up_games': join_up_games,
            'concluded_games': concluded_games,
        }
    )


@login_required()
def play(request, pk):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :param pk:
    :return:
    """
    game = get_object_or_404(Game, pk=pk)
    iterator = xrange(CONNECT4_SIZE)
    player, next_turn = game.player_context(request.user)
    if game.status == Game.Status.new:
        if game.player1 == request.user:
            return render(request, 'play/game_display.html', {'game': game, 'n': iterator})
        elif not game.join_up(request.user):
            raise PermissionDenied('Game is already complete.')
        else:
            return redirect('play_move', pk=pk)
    if not player:
        raise PermissionDenied('You are not a player of this game.')

    if game.status == Game.Status.finished:
        if player:
            return render(request, 'play/game_display.html', {'game': game, 'n': iterator})
    elif next_turn:
        return redirect('play_move', pk=pk)
    else:
        return render(request, 'play/game_display.html', {'game': game, 'n': iterator})


@login_required()
def new_game(request):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    game = GameManager.create_new_game(request.user)
    return redirect('play_game', pk=game.pk)


@login_required()
def play_next_move(request, pk):
    """
    write your view which controls the gameplay interaction w the web layer here
    :param request:
    :return:
    """
    game = get_object_or_404(Game, pk=pk)
    player, next_turn = game.player_context(request.user)
    if not next_turn:
        raise PermissionDenied('Not your turn to play.')
    context = {'game': game}
    if request.method == 'POST':
        form = NextMoveForm(data=request.post)
        context['form'] = form
        if form.is_valid():
            coin = form.save()
            game.update_game(coin, request.user)
            return redirect('play_game', pk=pk)
    else:
        context['form'] = NextMoveForm()
    return render(request, 'play/play_next_move.html', context)
