from mercurial import util
import sys
popen4 = util.popen4

class gitinforesolver(object):
    def __init__(self):
        self._revs = None

    def commitmessagefor(self, rev):
        return popen4("git cat-file commit %s | sed '1,/^$/d'" % rev)[1].read().strip()

    @property
    def revs(self):
        if self._revs:
            return self._revs
        raw = popen4('git rev-list %s..%s' %(self.old, self.new))[1].read().strip()
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
