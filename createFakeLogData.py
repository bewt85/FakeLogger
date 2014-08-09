import random, numpy, datetime

# Format
# ip_address userId dateTime "request" status page_size referer deviceFingerprint
# e.g.
# 123.123.123.123 user_12345 [01/Aug/2014:00:00:00] "GET /foo/bar.html" 200 500 "www.example.com/foo/baz.html" device_12345

class Customer(object):

  used_ips = []
  nextUserIndex = 1
  nextDeviceIndex = 1

  def __init__(self):
    self.ip = self.getNewRandomIp()
    self.userId = self.getNextUserId()
    self.deviceId = self.getNextDeviceId()

  def start(self, page, time=None):
    self.page = page
    self.time = time if time else datetime.datetime.now()
    self.history = []

  @classmethod
  def getNewRandomIp(cls):
    new_ip = "{}.{}.{}.{}".format(random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))
    while new_ip in cls.used_ips:
      new_ip = "{}.{}.{}.{}".format(random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))
    cls.used_ips.append(new_ip)
    return new_ip

  @classmethod
  def getNextUserId(cls):
    userId = "user_{:0{width}}".format(cls.nextUserIndex, width=8)
    cls.nextUserIndex += 1
    return userId

  @classmethod
  def getNextDeviceId(cls):
    deviceId = "device_{:0{width}}".format(cls.nextDeviceIndex, width=8)
    cls.nextDeviceIndex += 1
    return deviceId

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
      self.page = None
      return
    if not self.page.transitions:
      self.page = None
      return
    transition = self.pick(self.page.transitions, random.random())
    self.page = transition.destination
    self.time += datetime.timedelta(0,numpy.random.poisson(transition.timeBeforePageChange))
    self.history.append((self.time, transition))

  def createHistory(self, length=0):
    while self.page and (length > 0 or len(self.history <= length)):
      self.step()

  def formatHistory(self):
    for (transitionTime, transition) in self.history:
      if transition.destination == None:
        return
      logline_data = {
        "ip": self.ip,
        "user": self.userId,
        "time": transitionTime.strftime("[%d/%b/%Y:%H:%M:%S +0000]"),
        "method": transition.method,
        "destination": transition.destination.path,
        "status": transition.status,
        "size": transition.destination.size,
        "source": transition.source.domain + transition.source.path,
        "fingerprint": self.deviceId
      }
      yield (transitionTime, "{ip} {user} {time} \"{method} {destination}\" {status} {size} \"{source}\" {fingerprint}".format(**logline_data))

  def __repr__(self):
    return "User {}: ip = {}; device = {}".format(self.userId, self.ip, self.deviceId)

class Transition(object):
  def __init__(self, source, destination, method='GET', status=None, timeBeforePageChange=120.0):
    self.source = source
    self.destination = destination
    self.method = method
    self.timeBeforePageChange=120
    defaultStatus = {'GET': 200, 'POST': 201, 'PUT': 200}
    self.status = status if status else defaultStatus.get(method, 200)

  def __repr__(self):
    return "Transition: ({}) -> ({}) (method: {} status: {} in {} seconds)".format(
      self.source, self.destination, self.method, 
      self.status, self.timeBeforePageChange
    )

class Page(object):
  def __init__(self, path, size=None, domain=None, quitProb=0.001):
    self.path = path
    self.domain = domain if domain else "www.example.com"
    self.size = size if size else random.randint(200, 200000)
    self.quitProb = quitProb
    self.transitions = []

  def addNextPage(self, page, method='GET', status=None, timeBeforePageChange=120.0, likelyhoodWeight=1):
    self.transitions.append((likelyhoodWeight, Transition(self, page, method, status, timeBeforePageChange)))
  
  def __repr__(self):
    return "Page: <{},{}>".format(self.domain, self.path)

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

  class HistoryTest(unittest.TestCode):
    def setUp(self):
      self.customer = Customer()
      self.pageA = Page('/pageA', quitProb=0.0)
      self.pageB = Page('/pageB', quitProb=0.0)
    
    def test_singleTransition(self):
      self.pageA.addNextPage(self.pageB) 
      self.pageB.addNextPage(None)
      self.customer.start(pageA)
      self.customer.createHistory(10) 
      self.assertEqual(len(self.customer.history), 2)
      self.assertequal(self.customer.history[0][1].source, self.pageA)
      self.assertequal(self.customer.history[0][1].destination, self.pageB)
      self.assertequal(self.customer.history[1][1].source, self.pageB)
      self.assertequal(self.customer.history[1][1].destination, None)

  unittest.main()
