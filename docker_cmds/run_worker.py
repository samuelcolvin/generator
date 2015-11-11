#!/usr/bin/python3.5
import sys
import time
print('delaying worker start by 5 seconds...', file=sys.stderr, flush=True)
time.sleep(5)

sys.path.append('/src/gen')
from worker import Worker
Worker().run_forever()
