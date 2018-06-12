from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from .services import *
from django.views import generic
from django.core.urlresolvers import reverse_lazy


# Create your views here.

@login_required
def index(request):
    cards = Card.objects.filter(user=request.user)
    form = BookSearchForm
    if len(cards) == 0:
        return render(request, 'library/index_nocard.html', {
        'form': form,
        })
    for card in cards:
        update_book_on_card(card)
    books = Book.objects.filter(card__user=request.user, kind=0).order_by('duedate')
    return render(request, 'library/index.html', {
        'books': books,
        'form': form,
    })

@login_required
def renew(request):
    books = Book.objects.filter(card__user=request.user, kind=0, fine=None)
    for book in books:
        renew_book(book, request)
    messages.info(request, 'Renouvellement en masse terminé.')
    return redirect('index')

@login_required
def hold(request):
    cards = Card.objects.filter(user=request.user)
    if len(cards) == 0:
        return render(request, 'library/index_nocard.html')
    for card in cards:
        update_book_on_card(card)
    books = Book.objects.filter(card__user=request.user, kind=1).order_by('duedate')
    return render(request, 'library/hold.html', {
        'books': books,
    })

@login_required
def hold_cancel(request, pk):
    book = get_object_or_404(Book, pk=pk)
    cancel_hold(book, request)
    return redirect('hold')

@login_required
def search(request):
    if request.method == 'POST':
        form = BookSearchForm(request.POST)
        if form.is_valid():
            results = search_book(form.cleaned_data['search'], request)
            return render(request, 'library/search.html', {
                'results': results,
                'form': form,
            })
    return redirect('index')

@login_required
def book_reserve(request, code):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            reserve_book(form.instance, request)
            return redirect('index')
        else:
            book = search_book_info(code, request)
    else:
        book = search_book_info(code, request)
        form = BookForm(instance=book)

    formSearch = BookSearchForm
    return render(request, 'library/book_reserve.html', {
        #'results': results,
        'form': form,
        'formSearch': formSearch,
        'book': book,
    })

@login_required
def book_renew(request, pk):
    book = get_object_or_404(Book, pk=pk)
    renew_book(book, request)
    return redirect('index')

class CardIndexView(LoginRequiredMixin, generic.ListView):
    def get_queryset(self):
        """Return the card of the user."""
        return Card.objects.filter(user=self.request.user)

class CardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Card
    form_class = CardForm
    success_url = reverse_lazy('card_index')
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.lastrefresh = datetime.fromtimestamp(0)
        return super(CardCreateView, self).form_valid(form)

class CardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Card
    form_class = CardForm
    success_url = reverse_lazy('card_index')

class CardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Card
    success_url = reverse_lazy('card_index')
