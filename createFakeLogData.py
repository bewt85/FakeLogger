import random, numpy

# Format
# ip_address userId dateTime "request" status page_size deviceFingerprint
# e.g.
# 123.123.123.123 user_12345 [01/Aug/2014:00:00:00] "GET /foo/bar.html" 200 500 device_12345

numberOfCustomers = 1000

ipAddressPool = ["{}.{}.{}.{}".format(random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255)) for i in range(numberOfCustomers * 2)]
ipAddressPool = list(set(ipAddressPool))
getNewRandomIp = ipAddressPool.pop

userIdPool = ["user_{:0{width}}".format(i, width=8) for i in range(numberOfCustomers)]
getNextUserId = userIdPool.pop

deviceIdPool = ["device_{:0{width}}".format(i, width=8) for i in range(numberOfCustomers)]
getNextDeviceId = deviceIdPool.pop

class Customer(object):
  def __init__(self):
    self.ip = getNewRandomIp()
    self.userId = getNextUserId()
    self.deviceId = getNextDeviceId()

  def start(self, page, time):
    self.page = page
    self.time = time

  @classmethod
  def calculateCumulativeWeightedTransitions(cls, weighted_transitions):
    weights,transitions = [list(wt) for wt in zip(*weighted_transitions)]
    totalWeights = sum(weights)
    cumulativeWeights = [float(sum(weights[:i+1]))/totalWeights for (i,w) in enumerate(weights)]
    return zip(cumulativeWeights, transitions)

  @classmethod
  def pick(cls, weighted_transitions, p):
    cumulativeWeights = cls.calculateCumulativeWeightedTransitions(weighted_transitions) 
    for (cw, t) in cumulativeWeights:
      if p < cw:
        return t
    return t # Return last element if p = 1.0
 
  def step(self):
    if self.page.quitProb > random.random():
      return None
    if not self.page.transitions:
      return None
    transition = self.pick(self.page.transitions, random.random())
    self.page = transition.destination
    self.time += numpy.random.poisson(transition.timeBeforePageChange)
    self.history.append((self.time, transition))

  def __repr__(self):
    return "User {}: ip = {}; device = {}".format(self.userId, self.ip, self.deviceId)

class Transition(object):
  def __init__(self, source, destination, method='GET', status=None, timeBeforePageChange=120.0):
    self.source = source
    self.destinaton = destination
    self.method = method
    self.timeBeforePageChange=120
    defaultStatus = {'GET': 200, 'POST': 201, 'PUT': 200}
    self.status = status if status else defaultStatus.get(method, 200)

class Page(object):
  def __init__(self, url, size=None, domain=None, quitProb=0.001):
    self.url = url
    self.domain = "www.example.com"
    self.size = random.randint(200, 200000)
    self.quitProb = quitProb
    self.transitions = []

  def addNextPage(self, page, method='GET', status=None, timeBeforePageChange=120.0, likelyhoodWeight=1):
    self.transitions.append((likelyhoodWeight, Transition(self, page, method, status, timeBeforePageChange)))

if __name__ == "__main__":

  import unittest

  class CumulativeWeightTest(unittest.TestCase):
    def setUp(self):
      self.customer = Customer()
      self.pageA = Page('/pageA')
      self.pageB = Page('/pageB')

    def test_OneTransition(self):
      transitionAB = Transition(self.pageA, self.pageB)
      transitions = [(1, transitionAB)]
      self.assertEqual(self.customer.calculateCumulativeWeightedTransitions(transitions), [(1.0, transitionAB)]) 

    def test_TwoEqualTransitions(self):
      transitionAB = Transition(self.pageA, self.pageB)
      transitionBA = Transition(self.pageB, self.pageA)
      transitions = [(1, transitionAB), (1, transitionBA)]
      self.assertEqual(self.customer.calculateCumulativeWeightedTransitions(transitions), [(0.5, transitionAB), (1.0, transitionBA)]) 
  
  class PickTest(unittest.TestCase):
    def setUp(self):
      self.customer = Customer()
      self.pageA = Page('/pageA')
      self.pageB = Page('/pageB')

    def test_oneTransition(self):
      transitionAB = Transition(self.pageA, self.pageB)
      transitions = [(1, transitionAB)]
      self.assertEqual(self.customer.pick(transitions, 0.0), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 0.2), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 0.5), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 0.8), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 1.0), transitionAB)

    def test_TwoEqualTransitions(self):
      transitionAB = Transition(self.pageA, self.pageB)
      transitionBA = Transition(self.pageB, self.pageA)
      transitions = [(1, transitionAB), (1, transitionBA)]
      self.assertEqual(self.customer.pick(transitions, 0.0), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 0.2), transitionAB)
      self.assertEqual(self.customer.pick(transitions, 0.5), transitionBA)
      self.assertEqual(self.customer.pick(transitions, 0.8), transitionBA)
      self.assertEqual(self.customer.pick(transitions, 1.0), transitionBA)


  unittest.main()
