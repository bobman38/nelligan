from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^renew$', views.renew, name='renew'),
    url(r'^book/(?P<pk>[0-9]+)/renew$', views.book_renew, name='book_renew'),
    url(r'^hold$', views.hold, name='hold'),
    url(r'^card$', views.CardIndexView.as_view(), name='card_index'),
    url(r'^card/add$', views.CardCreateView.as_view(), name='card_add'),
    url(r'^card/(?P<pk>[0-9]+)$', views.CardUpdateView.as_view(), name='card_edit'),
    url(r'^card/(?P<pk>[0-9]+)/delete$', views.CardDeleteView.as_view(), name='card_delete'),
]
