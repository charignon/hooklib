import unittest
import time
from hooklib import hookrunner, basehook, parallelhookrunner
from hooklib_input import inputparser
from hooklib_git import *
from hooklib_hg import *
import os
import sys

class passinghook(basehook):
    def check(self, log, revdata):
        return True

ERROR_MSG = "ERROR ABC"
class failinghook(basehook):
    def check(self, log, revdata):
        log.write(ERROR_MSG)
        return False

ERROR_MSG2 = "ERROR XYZ"
class failinghook2(basehook):
    def check(self, log, revdata):
        log.write(ERROR_MSG2)
        return False

class slowfailinghook(basehook):
    def check(self, log, revdata):
        time.sleep(0.1)
        log.write(ERROR_MSG)
        return False

class testhookrunner(unittest.TestCase):

    def test_passing_hook(self):
        """Passing hook works"""
        runner = hookrunner()
        runner.register(passinghook)
        assert(runner.evaluate()) == True

    def test_failing_hook(self):
        """Failing hook fails with error message recorded"""
        runner = hookrunner()
        runner.register(failinghook)
        assert(runner.evaluate()) == False
        assert(runner.log.read()) == [ERROR_MSG]

    def test_passing_failing_hook(self):
        """Passing than failing hook, fails overall"""
        runner = hookrunner()
        runner.register(passinghook)
        runner.register(failinghook)
        assert(runner.evaluate()) == False

    def test_failing_stop_hook(self):
        """Two failing hook, second one should not run"""
        runner = hookrunner()
        runner.register(failinghook)
        runner.register(failinghook2)
        assert(runner.evaluate()) == False
        assert(runner.log.read()) == [ERROR_MSG]

    def test_failing_non_blocking_hook(self):
        """Two failing hook, non blocking, all evaluated"""
        runner = hookrunner()
        runner.register(failinghook, blocking=False)
        runner.register(failinghook2)
        assert(runner.evaluate()) == False
        assert(runner.log.read()) == [ERROR_MSG, ERROR_MSG2]

class testparallelhookrunner(unittest.TestCase):

    def test_speed(self):
        """parallel hook runner should run hooks really in parallel"""
        runner = parallelhookrunner()
        for i in range(100):
            runner.register(slowfailinghook)
        t1 = time.time()
        assert(runner.evaluate()) == False
        t2 = time.time()
        # 100 * 0.1 = 10s if the run was not parallel, here we expect less than 0.5s
        assert (t2-t1) < 0.5

    def test_aggregation(self):
        """parallel hook runner should aggregate log of all the failures"""
        runner = parallelhookrunner()
        for i in range(3):
            runner.register(slowfailinghook)
        runner.register(failinghook2)
        runner.evaluate()
        assert len(runner.log.read()) == 4
        assert ERROR_MSG2 in runner.log.read()

    def test_correctness(self):
        """parallel hook runner with failing and passing hook should return failure"""
        runner = parallelhookrunner()
        for i in range(3):
            runner.register(slowfailinghook)
        for i in range(3):
            runner.register(passinghook)
        assert(runner.evaluate() == False)

class testscmresolution(unittest.TestCase):
    """Checking that we get the right SCM parser for different hook type"""
    
    def setUp(self):
        self.origargv = list(sys.argv)
        self.origenv = os.environ.copy()

    def tearDown(self):
        os.environ = self.origenv
        sys.argv = self.origargv
    
    def test_git_postupdate(self):
        os.environ["GIT_DIR"] = "."
        sys.argv = ["program.name", "a"*40]
        revdata = inputparser.fromphase('post-update').parse()
        assert(revdata.revs == ["a"*40])
    
    def test_hg_postupdate(self):
        os.environ["HG_NODE"] = "."
        with self.assertRaises(NotImplementedError):
            revdata = inputparser.fromphase('post-update')

    def test_git_update(self):
        os.environ["GIT_DIR"] = "."
        sys.argv = ["program.name", "a"*40, "0"*40, "1"*40]
        revdata = inputparser.fromphase('update').parse()
        assert(revdata.refname == "a"*40)
        assert(revdata.old == "0"*40)
        assert(revdata.new == "1"*40)
    
    def test_hg_update(self):
        os.environ["HG_NODE"] = "a"*40
        revdata = inputparser.fromphase('update').parse()
        assert(revdata.revs == ["a"*40])
    
    def test_git_precommit(self):
        os.environ["GIT_DIR"] = "."
        sys.argv = ["program.name"]
        revdata = inputparser.fromphase('pre-commit').parse()
        assert(isinstance(revdata, gitinforesolver))

    def test_hg_precommit(self):
        os.environ["HG_NODE"] = "."
        with self.assertRaises(NotImplementedError):
            revdata = inputparser.fromphase('pre-commit')
    
    def test_unknown_hookname(self):
        with self.assertRaises(NotImplementedError):
            revdata = inputparser.fromphase('unknown-phase')

    def test_gitapplypatchmsg(self):
        sys.argv = ['program.name', 'messagefile']
        revdata = inputparser.fromphase('applypatch-msg').parse()
        assert(revdata.messagefile == 'messagefile')

    def test_gitpreapplypatch(self):
        parser = inputparser.fromphase('pre-applypatch')
        assert(isinstance(parser, gitpreapplypatchinputparser))
        assert(isinstance(parser.parse(), gitinforesolver))
    
    def test_gitpostapplypatch(self):
        parser = inputparser.fromphase('post-applypatch')
        assert(isinstance(parser, gitpostapplypatchinputparser))
        assert(isinstance(parser.parse(), gitinforesolver))

    def test_cascade_hook_type(self):
        """If you write a hook for hg and git and they don't
        have the same hook phase available, you can specify what
        phase you want for each SCM

        The following hook will run at the update phase for
        hg repos and post-applypatch for git repos
        A hg repo. If both are available the order of the tuple
        is honored.
        """
        os.environ["HG_NODE"] = "a"*40
        parser = inputparser.fromphases((('hg','update'), 
                                         ('git','post-applypatch')))
        assert(isinstance(parser, hgupdateinputparser))
        del os.environ["HG_NODE"]
        parser = inputparser.fromphases((('hg','update'), 
                                         ('git','post-applypatch')))
        assert(isinstance(parser, gitpostapplypatchinputparser))

    def test_cascade_hook_notfound(self):
        os.environ["HG_NODE"] = "a"*40
        with self.assertRaises(NotImplementedError):
            parser = inputparser.fromphases((('hg','post-applypatch'), 
                                             ('git','blah')))

    def test_gitpreparecommitmsg(self):
        # possible options
        # message, template, merge, squash, commit
        cases = (
                    # valid arg, list of args
                    (True, 'commitlogmsg', 'message'),
                    (False, 'commitlogmsg', 'message', 'a'*40),
                    (True, 'commitlogmsg', 'template'),
                    (False, 'commitlogmsg', 'template', 'a'*40),
                    (True, 'commitlogmsg', 'merge'),
                    (False, 'commitlogmsg', 'merge', 'a'*40),
                    (True, 'commitlogmsg', 'squash'),
                    (False, 'commitlogmsg', 'squash', 'a'*40),
                    (False, 'commitlogmsg', 'commit'),
                    (True, 'commitlogmsg', 'commit', 'a'*40),
                    (False, 'commitlogmsg', 'illegal'),
                )
        
        for case in cases:
            valid = case[0]
            args = case[1:]
            sys.argv = ['program.name'] + list(args)
            parser = inputparser.fromphase('prepare-commit-msg')
            assert(isinstance(parser, gitpreparecommitmsginputparser))
            if valid:
                parser.parse() # not exception
            else:
                with self.assertRaises(ValueError):
                    parser.parse()

    def test_gitcommitmsg(self):
        sys.argv = ['program.name', 'messagefile']
        revdata = inputparser.fromphase('commit-msg').parse()
        assert(revdata.messagefile == 'messagefile')

    def test_gitpostcommit(self):
        parser = inputparser.fromphase('post-commit')
        assert(isinstance(parser, gitpostcommitinputparser))

    def test_gitprerebase(self):
        sys.argv = ['program.name', 'upstream', 'rebased']
        parser = inputparser.fromphase('pre-rebase')
        assert(isinstance(parser, gitprerebaseinputparser))
        revdata = parser.parse()
        assert(revdata.upstream == 'upstream')
        assert(revdata.rebased == 'rebased')
 
    def test_gitprerebasecurrentbranch(self):
        sys.argv = ['program.name', 'upstream']
        parser = inputparser.fromphase('pre-rebase')
        assert(isinstance(parser, gitprerebaseinputparser))
        revdata = parser.parse()
        assert(revdata.upstream == 'upstream')
        assert(revdata.rebased == None)

    def test_gitpreautogc(self):
        parser = inputparser.fromphase('pre-auto-gc')
        assert(isinstance(parser, gitpreautogcinputparser))

    # TODO post-checkout, post-merge, pre-push, pre-receive, post-receive,
    # push-to-checkout, post-rewrite, rebase
    # see https://git-scm.com/docs/githooks

if __name__ == '__main__':
    unittest.main()
