from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^renew$', views.renew, name='renew'),
    url(r'^book/(?P<pk>[0-9]+)/renew$', views.book_renew, name='book_renew'),
    url(r'^search$', views.search, name='book_search'),
    url(r'^hold$', views.hold, name='hold'),
    url(r'^hold/(?P<pk>[0-9]+)/cancel$', views.hold_cancel, name='hold_cancel'),

    url(r'^book/reserve/(?P<code>.+)$', views.book_reserve, name='book_reserve'),

    url(r'^card$', views.CardIndexView.as_view(), name='card_index'),
    url(r'^card/add$', views.CardCreateView.as_view(), name='card_add'),
    url(r'^card/(?P<pk>[0-9]+)$', views.CardUpdateView.as_view(), name='card_edit'),
    url(r'^card/(?P<pk>[0-9]+)/delete$', views.CardDeleteView.as_view(), name='card_delete'),
]
