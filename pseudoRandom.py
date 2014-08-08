#!/usr/bin/env python

from hashlib import md5
import argparse, os, random

parser = argparse.ArgumentParser(description="Makes pseudo-random but deterministic files of ascii text")
parser.add_argument('output_file', help="Location of output file")
parser.add_argument('size', nargs='?', default=1024, type=int, help="Size in bytes of output file")
parser.add_argument('seed', nargs='?', default=None, help="A seed value to differentiate output files")
args = parser.parse_args()

args.seed = os.path.basename(args.output_file) if args.seed == None else args.seed

with open(args.output_file, 'w') as output_file:
  m = md5()
  for i in range(0, args.size-32, 32):
    m.update(args.seed)
    output_file.write(m.hexdigest())
  m.update(args.seed)
  output_file.write(m.hexdigest()[:args.size-(i+32)])
  
  for pos in sorted([random.randint(0, args.size) for i in range(0, args.size, 40)]):
    output_file.seek(pos)
    output_file.write('\n')

