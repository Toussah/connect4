from django.conf.urls import url
import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^signup/$', views.signup),
    url(r'^logout/$', views.logout),
    url(r'^games/$', views.games),
    url(r'^play/$', views.new_game),
    url(r'^play/(?P<pk>\d+)/$', views.play, name='play_game'),
    url(r'^play/(?P<pk>\d+)/play_move$', views.play_next_move, name='play_move'),
]
