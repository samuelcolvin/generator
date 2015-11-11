#!/usr/bin/python3.5
import sys
sys.path.append('/src/gen')

from worker import Worker
Worker().run_forever()
