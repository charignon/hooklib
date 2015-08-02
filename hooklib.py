"""Hook helpers library 

You can use this library to make it easier to write hooks that work with multiple
source control system (git, svn, hg ...).
It currently only works for git.
See https://github.com/charignon/hooklib for examples"""
import threading
import sys
from Queue import Queue
from hooklib_input import inputparser 

def runhooks(phase, hooks, parallel = False):
    if parallel:
        runner = parallelhookrunner(phase)
    else:
        runner = hookrunner(phase)
    for h in hooks:
        runner.register(h)
    ret = runner.evaluate()
    log = runner.log.read()
    if log:
        sys.stderr.write("\n".join(log)+"\n")
    if not ret:
        sys.exit(1)

class hooklog(object):
    """Collect logs from running hooks"""
    def __init__(self):
        self.msgs = []

    def write(self, msg):
        self.msgs.append(msg)

    def read(self):
        return self.msgs

    @staticmethod
    def aggregate(logs):
        msgs = []
        for l in logs:
            msgs.extend(l.read())
        ret = hooklog()
        ret.msgs = msgs
        return ret

class hookrunner(object):
    def __init__(self, phase=None, phases=None):
        self.runlist = []
        if phases is not None:
            self.revdata = inputparser.fromphases(phases).parse()
        else:
            self.revdata = inputparser.fromphase(phase).parse()

    def register(self, h, blocking=True):
        self.runlist.append((h, blocking))

    def evaluate(self):
        self.log = hooklog()
        success = True
        for h, blocking in self.runlist:
            hookpass = h().check(self.log, self.revdata)
            # Stop evaluating after failure on blocking hook
            if not hookpass and blocking:
                return False

            if not hookpass:
                success = False
        
        return success

class parallelhookrunner(hookrunner):
    def evaluateone(self, hook):
        log = hooklog()
        hookpass = hook().check(log, self.revdata)
        self.resultqueue.put((hookpass, log))

    def evaluate(self):
        threads = []
        self.resultqueue = Queue()
        for h, _ in self.runlist:
            t = threading.Thread(target=self.evaluateone, args=(h, ))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        res, logs = [], []
        
        for h in range(len(self.runlist)):
            r, l = self.resultqueue.get()
            res.append(r)
            logs.append(l)

        self.log = hooklog.aggregate(logs)
        return all(res)

 
class basehook(object):
    """A basehook is called for each rev that goes through, once with the revdata"""
    pass
