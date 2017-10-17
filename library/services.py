from datetime import datetime, timezone
from .models import Book
import requests
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
    if(tdiff.total_seconds() > 3600):
        # lets update lastrefresh first !
        card.lastrefresh = datetime.now(timezone.utc)
        card.save()

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
            book.kind = 0
            if duedate != None:
                duedate = duedate.rstrip().lstrip(" DUE ")
            # format date 17-09-25
            book.duedate = datetime.strptime(duedate, '%y-%m-%d')
            book.save()

        # Grab holds (reserved)
        for a in soup.findAll('a'):
            if '/holds' in a['href']:
                print(a['href'])
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
