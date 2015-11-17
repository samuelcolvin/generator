#!/usr/bin/python3.5
import sys
import time
from worker import Worker

print('delaying worker start by 5 seconds...', file=sys.stderr, flush=True)
time.sleep(5)
Worker().run_forever()
