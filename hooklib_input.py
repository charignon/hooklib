from hooklib_git import gitpostupdateinputparser
from hooklib_git import gitupdateinputparser
from hooklib_git import gitprecommitinputparser
from hooklib_git import gitpreapplypatchinputparser
from hooklib_git import gitapplypatchmsginputparser
from hooklib_git import gitpostapplypatchinputparser
from hooklib_git import gitcommitmsginputparser
from hooklib_git import gitpostcommitinputparser
from hooklib_git import gitprepushinputparser
from hooklib_git import gitprerebaseinputparser
from hooklib_git import gitpreautogcinputparser
from hooklib_git import gitprereceiveinputparser
from hooklib_git import gitpostreceiveinputparser
from hooklib_git import gitpreparecommitmsginputparser
from hooklib_hg import hgupdateinputparser
import os
import sys

def readlines():
    """Extracted to make mocking it easier"""
    return sys.stdin.readlines()

class prepushinputparser(object):
    @staticmethod
    def findscm():
        return gitprepushinputparser()


class prereceiveinputparser(object):
    @staticmethod
    def findscm():
        return gitprereceiveinputparser()

class postreceiveinputparser(object):
    @staticmethod
    def findscm():
        return gitpostreceiveinputparser()

class preparecommitmsginputparser(object):
    @staticmethod
    def findscm():
        return gitpreparecommitmsginputparser()

class preautogcinputparser(object):
    @staticmethod
    def findscm():
        return gitpreautogcinputparser()

class prerebaseinputparser(object):
    @staticmethod
    def findscm():
        return gitprerebaseinputparser()

class postcommitinputparser(object):
    @staticmethod
    def findscm():
        return gitpostcommitinputparser()

class preapplypatchinputparser(object):
    @staticmethod
    def findscm():
        return gitpreapplypatchinputparser()

class postapplypatchinputparser(object):
    @staticmethod
    def findscm():
        return gitpostapplypatchinputparser()

class applypatchmsginputparser(object):
    @staticmethod
    def findscm():
        return gitapplypatchmsginputparser()

class commitmsginputparser(object):
    @staticmethod
    def findscm():
        return gitcommitmsginputparser()

class postupdateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of postupdateinputparser based on the SCM used"""
        if 'GIT_DIR' in os.environ:
            return gitpostupdateinputparser()
        else:
            raise NotImplementedError("No implemented for your SCM")


class updateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of updateinputparser based on the SCM used"""
        if 'GIT_DIR' in os.environ:
            return gitupdateinputparser()
        elif 'HG_NODE' in os.environ:
            return hgupdateinputparser()
        else:
            raise NotImplementedError("No implemented for your SCM")

class precommitinputparser(object):
    @staticmethod
    def findscm():
        if 'GIT_DIR' in os.environ:
            return gitprecommitinputparser()
        else:
            raise NotImplementedError("No implemented for your SCM")

class dummyinputparser(object):
    @staticmethod
    def findscm():
        return dummyinputparser()
    def parse(self):
        return None

class inputparser(object):
    @staticmethod
    def fromphases(p):
        for scm, phasename in p:
            try:
                parserforphase = inputparser.fromphase(phasename)
                if parserforphase.scm() == scm:
                    return parserforphase
                else:
                    continue
            except NotImplementedError:
                pass
        raise NotImplementedError("Couldn't find phase matching"
                                  " conditions")

    @staticmethod
    def fromphase(phase):
        """Factory method to return an appropriate input parser
        For example if the phase is 'post-update' and that the git env
        variables are set, we infer that we need a git postupdate inputparser"""
        phasemapping = {
            None: dummyinputparser,
            'applypatch-msg': applypatchmsginputparser,
            'pre-applypatch': preapplypatchinputparser,
            'post-applypatch': postapplypatchinputparser,
            'pre-commit': precommitinputparser,
            'prepare-commit-msg': preparecommitmsginputparser,
            'commit-msg': commitmsginputparser,
            'post-commit': postcommitinputparser,
            'pre-rebase': prerebaseinputparser,
            'pre-push': prepushinputparser,
            'pre-receive': prereceiveinputparser,
            'update': updateinputparser,
            'post-receive': postreceiveinputparser,
            'post-update': postupdateinputparser,
            'pre-auto-gc': preautogcinputparser,
        }
        try:
            return phasemapping[phase].findscm()
        except KeyError:
            raise NotImplementedError("Unsupported hook type %s"%(phase))

