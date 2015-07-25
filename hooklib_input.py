from hooklib_git import gitpostupdateinputparser
from hooklib_git import gitupdateinputparser
from hooklib_git import gitinforesolver

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


