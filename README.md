# FakeLogger

FakeLogger is designed to make semi-realistic webserver logs.  It could be used
 for training or testing of fraud detection algorithms or systems which monitor
application performance.

FakeLogger works by creating a set of fictional pages and links between them. 
These links can have different weights, methods and return codes.  They also
have a `timeBeforePageChange` parameter which is used to make the time between
page visits more realistic.

Once you have a fake website, you create some fake customers and use them to 
create some fake history.

## Example usage

```python
from FakeLogger import *

# Create some pages
google = Page('/search', domain='www.google.com', quitProb=0.0)
startPage = Page('/start')
account = Page('/account/:userId')
buy = Page('/account/:userId/buy')
sell = Page('/account/:userId/sell')
survey = Page('/survey')
anotherWebsite = None

# Create links between pages
google.addNextPage(startPage)
startPage.addNextPage(account, timeBeforePageChange=30.0)
account.addNextPage(buy, method='POST')
account.addNextPage(sell, method='POST')
buy.addNextPage(survey, likelyhoodWeight=0.1)
buy.addNextPage(account)
buy.addNextPage(anotherWebsite)
sell.addNextPage(survey, likelyhoodWeight=0.3)
sell.addNextPage(account)
sell.addNextPage(anotherWebsite)
survey.addNextPage(account)

# This creates normally distributed start times around lunch
def randomStartTime():
  now = datetime.datetime.now()
  HOURS = 60*60
  random_offset = datetime.timedelta(0, random.gauss(12*HOURS, 2*HOURS))
  return datetime.datetime(now.year, now.month, now.day) + random_offset

all_history = []
for customer in (Customer() for i in range(1000)):
  customer.start(google, time=randomStartTime()) # Set a starting point for the journey
  customer.createHistory() # This creates the history as (timestamp, Transition) tuples
  # formatHistory turns the transitions into log lines
  all_history += list(customer.formatHistory())

first = lambda t: t[0] # Selects the timestamp from history
second = lambda t: t[1] # Selects the log line from history

sorted_history = sorted(all_history, key=first) # Get customer history in order
for line in map(second, sorted_history): # We only want to print the log lines
  print line
```

## Potential Extensions
- log users in and out
- log users out automatically if they're a bit slow
- add fraudulent customers for example:
  - attempt to access /admin page
  - spend a lot less time on each page
  - access pages in a strange order
- simulate broken / slow components in web stack
