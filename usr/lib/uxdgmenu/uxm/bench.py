import time
from collections import OrderedDict

class Bench(object):
    def __init__(self):
        self.steps = OrderedDict()
        self.timer = time.clock

    def start(self):
        self.start = self.timer()
        self.steps['__global__'] = {
            'start': {
                'time': 0,
                'message': 'global startup'
            }
        }
    def stop(self):
        t = self.timer() - self.start
        self.steps['__global__']['end'] = {
            'time': t,
            'message': 'global shutdown'
        }

    def step(self, id, msg=""):
        t = self.timer() - self.start
        self.steps[id] = {
            'start': {'time':t,'message':msg}
        }

    def endstep(self, id, msg=""):
        t = self.timer() - self.start
        self.steps[id]['end'] = {'time':t,'message':msg}

    def print_results(self):
        for id, step in self.steps.iteritems():
            print "\n%s" % ("=" * 70)
            print "Bench %s" % id
            start, end = step['start'], step['end']
            print ">>> Start  %.3f %s" % (start['time'], start['message']) 
            print ">>> End    %.3f %s" % (end['time'], end['message'])
            print ">>> Time   %.3f" % (end['time'] - start['time'])

UID = int(time.time())
_bench = Bench()
_bench.start()

def step(id, msg=""):
    _bench.step(id, msg)
def endstep(id, msg=""):
    _bench.endstep(id, msg)
def stop():
    _bench.stop()

def id():
    return hex(UID+1)

def results():
    _bench.print_results()
