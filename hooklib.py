import threading
import sys
from Queue import Queue

class hooklog(object):
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

class gitpostupdateinputparser(object):
    def parse(self):
        revs = sys.argv[1:]
        return {'revs': revs}

class gitupdateinputparser(object):
    def parse(self):
        name, old, new = sys.argv[1:]
        return {'name': name,
                'old': old,
                'new': new}

class postupdateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of postupdateinputparser based on the SCM used"""
        return gitpostupdateinputparser()

class updateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of updateinputparser based on the SCM used"""
        return gitupdateinputparser()


class dummyinputparser(object):
    def parse(self):
        return None

class inputparser(object):
    @staticmethod
    def fromphase(phase):
        """Factory method to return an appropriate input parser
        For example if the phase is 'post-update' and that the git env
        variables are set, we infer that we need a git postupdate inputparser"""
        if phase == None:
            return dummyinputparser()
        elif phase == 'post-update':
            return postupdateinputparser.findscm()
        elif phase == 'update':
            return updateinputparser.findscm()
        else:
            raise Exception("Unsupported hook type %s"%(phase))


class hookrunner(object):
    def __init__(self, phase=None):
        self.runlist = []
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
