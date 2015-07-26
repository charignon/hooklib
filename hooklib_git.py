from mercurial import util
import sys
import os

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

class gitpostupdateinputparser(object):
    def parse(self):
        revs = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.setrevs(revs)
        return resolver

class gitupdateinputparser(object):
    def parse(self):
        refname, old, new = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.refname = refname
        resolver.old = old
        resolver.new = new
        return resolver

class gitprecommitinputparser(object):
    def parse(self):
        resolver = gitinforesolver()
        return resolver


