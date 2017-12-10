from datetime import datetime, timezone
from .models import Book
import requests
from django.contrib import messages
from bs4 import BeautifulSoup
NELLIGAN_URL = 'https://nelligan.ville.montreal.qc.ca'

def check_card(code, pin):
    login = {'code': code, 'pin': pin}
    r = requests.post(NELLIGAN_URL + '/patroninfo/?', data = login)
    #print(r.text)
    return not "Sorry, the information you submitted was invalid. Please try again." in r.text

def update_book_on_card(card):
    tdiff = datetime.now(timezone.utc) - card.lastrefresh

    # check if we need to update the card based on the lst update time
    if(tdiff.total_seconds() > 600):

        # if yes then purge all existing book on the card
        Book.objects.filter(card=card).delete()

        # grab again the book on the card from Nelligan website
        login = {'code': card.code, 'pin': card.pin}
        s = requests.session()
        r = s.post(NELLIGAN_URL + '/patroninfo/?', data = login)
        #print(r.text)
        # Grab loans (currently taken)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.select("tr.patFuncEntry")
        for item in items:
            book = Book()
            book.card = card
            book.barcode = item.select_one("td.patFuncBarcode").text
            book.name = item.select_one("span.patFuncTitleMain").string
            duedate = item.select_one("td.patFuncStatus").text
            #print(duedate)
            book.kind = 0
            if duedate != None:
                duedate = duedate.rstrip().lstrip(" DUE ")
                renewed = duedate[10:]
                duedate = duedate[:8]
                renewed = renewed.lstrip('Renewed ').rstrip('s').rstrip(' time')
            # format date 17-09-25
            #print(renewed)
            #print(duedate)
            if renewed != '':
                book.renewed = renewed
            book.duedate = datetime.strptime(duedate, '%y-%m-%d')
            book.save()

        # Grab holds (reserved)
        for a in soup.findAll('a'):
            if '/holds' in a['href']:
                #print(a['href'])
                r = s.get(NELLIGAN_URL + a['href'])
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select("tr.patFuncEntry")
                for item in items:
                    book = Book()
                    book.card = card
                    book.name = item.select_one("span.patFuncTitleMain").string
                    book.pickup = item.select_one("td.patFuncPickup").string
                    duedate = item.select_one("td.patFuncCancel").text
                    book.kind = 1
                    # format date 17-09-25
                    book.duedate = datetime.strptime(duedate, '%y-%m-%d')
                    book.save()

        # lets update lastrefresh first !
        card.lastrefresh = datetime.now(timezone.utc)
        card.save()

def renew_book(book, request):
    card = book.card

    # connect to nelligan
    login = {'code': card.code, 'pin': card.pin}
    s = requests.session()
    r = s.post(NELLIGAN_URL + '/patroninfo/?', data = login)
    #print(r.url)
    # soup the thing
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select("tr.patFuncEntry")
    for item in items:
        if(book.barcode == item.select_one("td.patFuncBarcode").text):
            # we are on the right book to renew
            book_value = item.select_one("td.patFuncMark input").attrs['value']
            book_id = item.select_one("td.patFuncMark input").attrs['id']

            # launch the query to renew this book
            r = s.post(r.url, data = {book_id: book_value})
            print(r.text)

            # now scan to get the renew date
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select("tr.patFuncEntry")
            for item in items:
                if(book.barcode == item.select_one("td.patFuncBarcode").text):
                    duedate = item.select_one("td.patFuncStatus").text
                    if("ON HOLD" in duedate):
                        messages.warning(request, 'Renouvellement impossible, livre reservé.')
                    elif("TOO SOON TO RENEW" in duedate):
                        messages.info(request, 'Renouvellement impossible, trop tôt !')
                    else:
                        # TOCHECK THIS PART ! not the same as classic book
                        # classic string  DUE 17-12-23 <em><b>  RENEWED</b><br />Now due 18-01-05</em> <span  class="patFuncRenewCount">Renewed 1 time</span>

                        duedate = item.select_one("td.patFuncStatus em").text
                        #print(duedate)
                        if duedate != None:
                            duedate = duedate.rstrip().lstrip("RENEWEDNow due ")
                            duedate = duedate[:8]
                        # format date 17-09-25
                        #print(duedate)
                        book.duedate = datetime.strptime(duedate, '%y-%m-%d')
                        book.save()
                        messages.success(request, 'Renouvellement effectué !')

