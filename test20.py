import requests
from bs4 import BeautifulSoup

NELLIGAN_URL = 'https://nelligan.ville.montreal.qc.ca'
class Book:
    def __init__(self, user, name, duedate):
        self.user, self.name, self.duedate = user, name, duedate
    def __repr__(self):
     return "%s - %s (%s)\n" % (self.duedate, self.name, self.user)

logins = {
        'sidonie':{'code':'12777390605961', 'pin':'123456'},
        #'eliott':{'code':'12777390606092', 'pin':'1203641'},
        #'marion':{'code':'12777390606100', 'pin':'1203641'},
        #'marcus':{'code':'12777390763596', 'pin':'1203641'},
        #'julien':{'code':'12777390668332', 'pin':'50825082'},
}
books = []

for user,login in logins.items():
    s = requests.session()
    r = s.post(NELLIGAN_URL + '/patroninfo/?', data = login)
    #print(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    #print(soup.find_all("table", class_="patFunc"))
    items = soup.select("tr.patFuncEntry")
    #print(items)
    for item in items:
        title = item.select_one("span.patFuncTitleMain").string
        duedate = item.select_one("td.patFuncStatus").text
        if duedate != None:
            duedate = duedate.rstrip().lstrip(" DUE ")
        book = Book(user, title, duedate)
        books.append(book)

    for a in soup.findAll('a'):
        if '/holds' in a['href']:
            print(a['href'])
            r = s.get(NELLIGAN_URL + a['href'])
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select("tr.patFuncEntry")
            for item in items:
                title = item.select_one("span.patFuncTitleMain").string
                print(title)


# sort list by DUE date
books.sort(key=lambda x: x.duedate, reverse=False)

print(books)
