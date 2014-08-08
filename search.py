import re

filename = "shortTest.txt"
search_string = re.compile('bbb')

matchingLineMap = lambda line: 1 if search_string.search(line) else 0

with open(filename, 'r') as f:
  text = f.read().split('\n')

print "Starting search"
matchingLineCount = sum(map(matchingLineMap, text))
