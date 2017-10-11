"""Example app to login to GitHub using the StatefulBrowser class."""

from __future__ import print_function
import mechanicalsoup

browser = mechanicalsoup.StatefulBrowser(
    soup_config={'features': 'lxml'},
    raise_on_404=True,
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
)
# Uncomment for a more verbose output:
browser.set_verbose(2)

browser.open("https://nelligan.ville.montreal.qc.ca/patroninfo/?")
#browser.follow_link("login")
browser.launch_browser()
browser.select_form('form')
browser["code"] = '12777390605961'
browser["pin"] = '123456'
resp = browser.submit_selected()

# Uncomment to launch a web browser on the current page:
browser.launch_browser()

# verify we are now logged in
page = browser.get_current_page()
messages = page.find("div", class_="flash-messages")
if messages:
    print(messages.text)
assert page.select(".logout-form")

print(page.title.text)

# verify we remain logged in (thanks to cookies) as we browse the rest of
# the site
page3 = browser.open("https://github.com/MechanicalSoup/MechanicalSoup")
assert page3.soup.select(".logout-form")
