from mercurial import util
import os

class basehginputparser(object):
    def scm(self):
        return 'hg'

class hginforesolver(basehginputparser):
    def commitmessagefor(self, rev):
        return util.popen4("hg log -r %s -T {desc}" % rev)[1].read()

class hgupdateinputparser(basehginputparser):
    def parse(self):
        rev = os.environ['HG_NODE']
        resolver = hginforesolver()
        resolver.revs = [rev]
        return resolver
