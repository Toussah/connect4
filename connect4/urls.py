from django.conf.urls import url
import views

urlpatterns = [
    url(r'^login/$', views.login),
    url(r'^signup/$', views.signup),
    url(r'^logout/$', views.logout),
    url(r'^games/$', views.games),
    url(r'^play/$', views.play),
]
