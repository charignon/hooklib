"""Package containing all the input parsers specific to git
Their implementation match what is described at https://git-scm.com/docs/githooks"""

from mercurial import util
import hooklib_input
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
        else:
            self.reporoot = util.popen4("git rev-parse --show-toplevel")[1].read().strip()

        self._revs = None

    def commitmessagefor(self, rev):
        return util.popen4("git cat-file commit %s | sed '1,/^$/d'" % rev)[1].read().strip()

    @property
    def head(self):
        return util.popen4("git rev-parse HEAD")[1].read().strip()

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
    """Input parser for the 'post-update' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD
    - revs (list of sha1 (str))"""
    def parse(self):
        revs = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.setrevs(revs)
        return resolver

class gitupdateinputparser(basegitinputparser):
    """Input parser for the 'update' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD
    - refname (str) => refname that is updated, like 'refs/heads/master'
    - old (str) => old sha of the ref
    - new (str) => new sha of the ref"""
    def parse(self):
        refname, old, new = sys.argv[1:]
        resolver = gitinforesolver()
        resolver.refname = refname
        resolver.old = old
        resolver.new = new
        return resolver

class gitprecommitinputparser(basegitinputparser):
    """Input parser for the 'pre-commit' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpreapplypatchinputparser(basegitinputparser):
    """Input parser for the 'pre-applypatch' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpostapplypatchinputparser(basegitinputparser):
    """Input parser for the 'post-applypatch' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpostcommitinputparser(basegitinputparser):
    """Input parser for the 'post-commit' phase

    Available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitpreautogcinputparser(basegitinputparser):
    """input parser for the 'pre-autogc' phase

    available fields:
    - reporoot (str) => root of the repo
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        return resolver

class gitreceiveinputparser(basegitinputparser):
    def parse(self):
        resolver = gitinforesolver()
        rawrevs = hooklib_input.readlines()
        revs = tuple([tuple(line.strip().split(' ')) for line in rawrevs])
        resolver.receivedrevs = revs
        return resolver

class gitpostreceiveinputparser(gitreceiveinputparser):
    """input parser for the 'post-receive' phase

    available fields:
    - reporoot (str) => root of the repo
    - receivedrevs =>
        (list of tuples: (<old-value> <new-value> <ref-name>))
    - head (str) => sha1 of HEAD"""
    pass

class gitprereceiveinputparser(gitreceiveinputparser):
    """input parser for the 'pre-receive' phase

    available fields:
    - reporoot (str) => root of the repo
    - receivedrevs =>
        (list of tuples: (<old-value> <new-value> <ref-name>))
    - head (str) => sha1 of HEAD"""
    pass

class gitprepushinputparser(basegitinputparser):
    """input parser for the 'pre-push' phase

    available fields:
    - reporoot (str) => root of the repo
    - revstobepushed =>
        (list of tuples: <local ref> <local sha1> <remote ref> <remote sha1>))
    - head (str) => sha1 of HEAD"""
    def parse(self):
        resolver = gitinforesolver()
        rawrevs = hooklib_input.readlines()
        revs = tuple([tuple(line.strip().split(' ')) for line in rawrevs])
        resolver.revstobepushed = revs
        return resolver

class gitapplypatchmsginputparser(basegitinputparser):
    """input parser for the 'applypatch-msg' phase

    available fields:
    - reporoot (str) => root of the repo
    - messagefile (str) => filename of the file containing the commit message
    - head (str) => sha1 of HEAD"""
    def parse(self):
        messagefile = sys.argv[1]
        resolver = gitinforesolver()
        resolver.messagefile = messagefile
        return resolver

class gitprerebaseinputparser(basegitinputparser):
    """input parser for the 'pre-rebase' phase

    available fields:
    - reporoot (str) => root of the repo
    - upstream (str) => upstream from which the serie was forked
    - rebased (str) => branch being rebased, None if current branch
    - head (str) => sha1 of HEAD"""
    def parse(self):
        upstream = sys.argv[1]
        if len(sys.argv) > 2:
            rebased = sys.argv[2]
        else:
            rebased = None
        resolver = gitinforesolver()
        resolver.upstream = upstream
        resolver.rebased = rebased
        return resolver

class gitcommitmsginputparser(basegitinputparser):
    """input parser for the 'commit-msg' phase

    available fields:
    - reporoot (str) => root of the repo
    - messagefile (str) => filename of the file containing the commit message
    - head (str) => sha1 of HEAD"""
    def parse(self):
        messagefile = sys.argv[1]
        resolver = gitinforesolver()
        resolver.messagefile = messagefile
        return resolver

class gitpreparecommitmsginputparser(basegitinputparser):
    """input parser for the 'prepare-commit-msg' phase

    available fields:
    - reporoot (str) => root of the repo
    - messagefile (str) => filename of the file containing the commit message
    - mode (str) =>  could be one of (None, 'message', 'template', 'merge', 'squash', 'commit')
    - sha (str) =>  could be a sha1 or None, relevant only when mode is 'commit'
    - head (str) => sha1 of HEAD"""
    def parse(self):
        messagefile = sys.argv[1]
        mode = None
        sha = None
        if len(sys.argv) > 2:
            mode = sys.argv[2]
        if len(sys.argv) > 3:
            sha = sys.argv[3]
        if (mode is not None and 
            mode not in ('message', 'template', 'merge', 'squash', 'commit')):
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

