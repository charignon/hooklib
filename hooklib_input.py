from hooklib_git import gitpostupdateinputparser
from hooklib_git import gitupdateinputparser
from hooklib_git import gitprecommitinputparser
from hooklib_hg import hgupdateinputparser
import os

class postupdateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of postupdateinputparser based on the SCM used"""
        if 'GIT_DIR' in os.environ:
            return gitpostupdateinputparser()
        else:
            raise Exception("No implemented for your SCM")


class updateinputparser(object):
    @staticmethod
    def findscm():
        """Find the correct type of updateinputparser based on the SCM used"""
        if 'GIT_DIR' in os.environ:
            return gitupdateinputparser()
        elif 'HG_NODE' in os.environ:
            return hgupdateinputparser()
        else:
            raise Exception("No implemented for your SCM")

class precommitinputparser(object):
    @staticmethod
    def findscm():
        if 'GIT_DIR' in os.environ:
            return gitprecommitinputparser()
        else:
            raise Exception("No implemented for your SCM")


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
        elif phase == 'pre-commit':
            return precommitinputparser.findscm()
        else:
            raise Exception("Unsupported hook type %s"%(phase))


