from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
from .models import Book, Card
import requests
from django.contrib import messages
from bs4 import BeautifulSoup
import time
import re

NELLIGAN_URL = 'https://nelligan.ville.montreal.qc.ca'

def check_card(code, pin):
    login = {'code': code, 'pin': pin}
    r = requests.post(NELLIGAN_URL + '/patroninfo/?', data = login)
    # print(r.text)
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
        # print(r.text)
        # Grab loans (currently taken)
        soup = BeautifulSoup(r.text, 'html.parser')
        items = soup.select("tr.patFuncEntry")
        for item in items:
            book = Book()
            book.card = card
            book.barcode = item.select_one("td.patFuncBarcode").text
            book.name = item.select_one("span.patFuncTitleMain").string[:200]
            duedate = item.select_one("td.patFuncStatus").text
            # print(duedate)
            book.kind = 0
            if duedate != None:
                due, renewed, fine = duedate_book(duedate)
            book.renewed = renewed
            book.fine = fine
            book.duedate = datetime.strptime(due, '%y-%m-%d')
            book.duedate = book.duedate.replace(tzinfo=timezone.utc)
            book.save()

        # search for fines
        card.fine = None
        fine = soup.select_one('span.pat-transac a')
        if fine != None:
            card.fine = fine.text
            #print(card.label + ": " + fine.text)

        # Grab holds (reserved)
        for a in soup.findAll('a'):
            if '/holds' in a['href']:
                #print(a['href'])
                r = s.get(NELLIGAN_URL + a['href'])
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select("tr.patFuncEntry")

                #if card.label == 'sidonie':
                #    print(soup.prettify())
                for item in items:
                    book = Book()
                    book.card = card

                    book.name = item.select_one("span.patFuncTitleMain").string
                    book.status = item.select_one("td.patFuncStatus").string
                    book.pickup = item.select_one("td.patFuncPickup").string
                    book.barcode = item.find('input', type='checkbox')['id']
                    duedate = item.select_one("td.patFuncCancel").text
                    book.kind = 1
                    # format date 17-09-25
                    book.duedate = datetime.strptime(duedate, '%y-%m-%d')
                    book.save()

        # lets update lastrefresh first !
        card.lastrefresh = datetime.now(timezone.utc)
        card.save()

def duedate_book(duedate):
    regexp = ' DUE (?P<due>\d{2}-\d{2}-\d{2})(?: FINE\(up to now\) (?P<fine>.*)\$)?(?:  Renewed (?P<renew>\d) times?)?'
    m = re.search(regexp, duedate)
    duedate = m.group('due')
    renewed = m.group('renew')
    if renewed is None:
        renewed = 0
    else:
        renewed = int(renewed)
    fine = m.group('fine')

    return duedate, renewed, fine

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
                        messages.warning(request, book.name + ': Renouvellement impossible, livre reservé.')
                    elif("TOO SOON TO RENEW" in duedate):
                        messages.info(request, book.name + ': Renouvellement impossible, trop tôt !')
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
                        book.renewed = book.renewed +1
                        book.duedate = datetime.strptime(duedate, '%y-%m-%d')
                        book.save()
                        messages.success(request, book.name + ': Renouvellement effectué !')

def search_book(value, request):
    results = []
    # run the search (no auth needed !)
    # see also '/search~S9/?searchtype=t&searcharg='
    r = requests.get(NELLIGAN_URL + '/search/a?searchtype=Y&searcharg=' + value)
    # soup the thing
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.prettify())
    for result_row in soup.find_all('table', {"class" : "browseSearchtoolMessage"}):
        #if result
        #print("\n\n\n" + result_row.prettify())
        result = {
    		'code': result_row.find('input').attrs['value'],
            'title': result_row.find('span','brief-lien-titre').find('a').text
    	}
        results.append(result)
    return results

def search_book_info(code, request):
    book = Book
    book.code = code
    book.localisation = []
    # book info (no auth needed !)
    r = requests.get(NELLIGAN_URL + '/record=' + code)
    # soup the thing
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.prettify())
    #print(soup.find("strong").prettify())
    book.name = soup.find("strong").text
    book.fullname = book.name
    reserve_link = soup.find('img', alt="Reserve this item").parent['href']
    #print(soup.find_all('tr', {"class": "bibItemsEntry"}))
    for result_row in soup.find_all('tr', {"class": "bibItemsEntry"}):
        #if result
        children = result_row.find_all('td')
        result = {
    		'localisation': children[0].text,
            'status': children[3].text,
    	}
        book.localisation.append(result)
    #print(results)

    #r = requests.get(NELLIGAN_URL + reserve_link)
    book.reserve_link = reserve_link
    #soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.prettify())
    return book

def reserve_book(book, request):
    #print(book.reserve_link)
    # set due date
    book.duedate = date.today() + relativedelta(months=+6)
    # set kind
    book.kind = 1
    # set name
    book.name = book.fullname
    book.pickup = book.library.name
    data = {
        'code': book.card.code,
        'pin': book.card.pin,
        'locx00' : book.library.code,
        'needby_Year': book.duedate.year,
        'needby_Month': book.duedate.month,
        'needby_Day': book.duedate.day,
    }
    print('data: ' + str(data))
    r = requests.post(NELLIGAN_URL + book.reserve_link, data=data)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.prettify())
    error = soup.find('div', style='color:red; font-size:x-large')
    if(error != None):
        messages.warning(request, book.fullname + ': Réservation impossible, livre déjà reservé. (' + error.text + ')' )
    success = soup.find('td', class_='main-biblio')
    if("was successful." in success.text):
        messages.info(request, book.fullname + ': Réservation effectuée !')
        book.save()
    return book

def cancel_hold(book, request):
    print('barcode: ' + book.barcode)

    # login Nelligan
    login = {'code': book.card.code, 'pin': book.card.pin}
    s = requests.session()
    r = s.post(NELLIGAN_URL + '/patroninfo/?', data = login)
    soup = BeautifulSoup(r.text, 'html.parser')

    for a in soup.findAll('a'):
        if '/holds' in a['href']:
            #print(a['href'])
            data = {
                'updateholdssome': 'YES',
                'currentsortorder': 'current_pickup',
                book.barcode: 'on',
                book.barcode.replace('cancel', 'loc'): '',
                'holdpagecmd': None
            }
            #print('data: ' + str(data))
            r = s.post(NELLIGAN_URL + a['href'], data = data)
            messages.info(request, book.name + ': Réservation annulée !')
            book.delete()
    return book