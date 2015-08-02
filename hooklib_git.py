from mercurial import util
import sys
import os

class basegitinputparser(object):
    def scm(self):
        return 'git'

class gitinforesolver(object):
    def __init__(self):
        self.reporoot = None
        if 'GIT_DIR' in os.environ:
            self.reporoot = os.path.dirname(os.path.abspath(os.environ["GIT_DIR"]))
        self._revs = None

    def commitmessagefor(self, rev):
        return util.popen4("git cat-file commit %s | sed '1,/^$/d'" % rev)[1].read().strip()

    @property
    def revs(self):
        if self._revs:
            return self._revs
        raw = util.popen4('git rev-list %s..%s' %(self.old, self.new))[1].read().strip()
        if raw != '':
            return raw.split("\n")
        else:
            return []
    
    def setrevs(self, revs):
        self._revs = revs

class gitpostupdateinputparser(basegitinputparser):
    def parse(self):
        revs = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.setrevs(revs)
        return resolver

class gitupdateinputparser(basegitinputparser):
    def parse(self):
        refname, old, new = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.refname = refname
        resolver.old = old
        resolver.new = new
        return resolver

class gitprecommitinputparser(basegitinputparser):
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpreapplypatchinputparser(basegitinputparser):
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpostapplypatchinputparser(basegitinputparser):
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpostcommitinputparser(basegitinputparser):
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitapplypatchmsginputparser(basegitinputparser):
    def parse(self):
        messagefile = sys.argv[1]
        resolver = gitinforesolver()
        resolver.messagefile = messagefile
        return resolver

class gitcommitmsginputparser(basegitinputparser):
    def parse(self):
        messagefile = sys.argv[1]
        resolver = gitinforesolver()
        resolver.messagefile = messagefile
        return resolver

class gitpreparecommitmsginputparser(basegitinputparser):
    def parse(self):
        messagefile = sys.argv[1]
        mode = None
        sha = None
        if len(sys.argv) > 2:
            mode = sys.argv[2]
        if len(sys.argv) > 3:
            sha = sys.argv[3]
        if mode not in ('message', 'template', 'merge', 'squash', 'commit'):
            raise ValueError('Invalid Second Argument: mode')
        if mode != 'commit' and sha is not None:
            raise ValueError('Invalid Third Argument')
        if mode == 'commit' and sha is None:
            raise ValueError('Missing Third Argument')
        resolver = gitinforesolver()
        resolver.messagefile = messagefile
        resolver.mode = mode
        resolver.sha = sha
        return resolver

