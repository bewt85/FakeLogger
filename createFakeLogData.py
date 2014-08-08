import random

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

  def __repr__(self):
    return "User {}: ip = {}; device = {}".format(self.userId, self.ip, self.deviceId)

if __name__ == "__main__":
  for customer in [Customer() for i in range(10)]:
    print customer    
