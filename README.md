# hooklib: write source control hooks in Python

Python hook helper library:
- SCM Agnostic: Can work with different SCM (git, svn, hg), write your hook once and they work on other SCMs
- Simple API: Don't learn the secret commands to peek inside your source control system, all you need is accessible and computed on the fly
- Parallel/Sequential mode: Run your hooks in parallel or sequentially

Supported hooks phases:

Phase name  | SCM
------------- | -------------
applypatch-msg  | Git
pre-applypatch  | Git
post-applypatch  | Git
pre-commit  | Git
prepare-commit-msg  | Git
commit-msg  | Git
post-commit  | Git
pre-rebase  | Git
pre-push  | Git
pre-receive  | Git
update  | Git, Hg
post-receive  | Git
post-update  | Git
pre-auto-gc  | Git

Currently only supports git and hg


Example 1: gate commit on commit message format
-
Feel free to compare this to how you would do this without this library: https://git-scm.com/book/en/v2/Customizing-Git-An-Example-Git-Enforced-Policy

This hooks works for both git and hg:
 - for git: put it in .git/hooks/update and make it executable for git
 - for hg: put it wherever your want and reference it from your hg config

```python
#!/usr/bin/python
from hooklib import basehook, runhooks

class commmitmsggatinghook(basehook):
   def check(self, log, revdata):
       for rev in revdata.revs:
           if not 'secretmessage' in revdata.commitmessagefor(rev):
               log.write("commit message must contain 'secretmessage'")
               return False
       return True

runhooks('update', hooks=[commmitmsggatinghook])
```

Example 2: only authorize push to master
-

_Contrary to the example 1, here we reference 'refs/heads/master', a git concept => this hook wouldn't work without code change for hg._
Save the following file under .git/hooks/update and make it executable to test it: 
 ```python
 #!/usr/bin/python
 from hooklib import basehook, runhooks
  
 class mastergatinghook(basehook):
    def check(self, log, revdata):
       pushtomaster = revdata['name'] == 'refs/heads/master'
       if not pushtomaster:           
          log.write("you can only push master on this repo")
          return False
       else:
          return True
  
 runhooks('update', hooks=[mastergatinghook])
  ```
  
Example 3: parallel execution
-
Save the following file under .git/hooks/post-update and make it executable to test it: 
  ```python
  #!/usr/bin/python
  from hooklib import basehook, runhooks
  import time
  
  class slowhook(basehook):
     def check(self, log, revdata):
         time.sleep(0.1)
         return True
  
  class veryslowhook(basehook):
     def check(self, log, revdata):
         time.sleep(0.5)
         return True

  # should take roughly as long as the slowest, i.e. 0.5s
  runhooks('post-update', hooks=[slowhook]*200+[veryslowhook], parallel=True)
  ```

Example 4: client side commit message styling check
-
The following hooks checks on the client side that the commit message follows the format: "topic: explanation"
I have it enabled for this repo to make sure that I respect the format I intended to keep.
Save the following file under .git/hooks/commit-msg and make it executable to test it:
  ```python
  #!/usr/bin/python 
  from hooklib import basehook, runhooks 
  import re
  
  class validatecommitmsg(basehook): 
       def check(self, log, revdata): 
  	with open(revdata.messagefile) as f:
  	    msg = f.read()
  	if re.match("[a-z]+: .*", msg):
  	    return True
  	else:
  	    log.write("validatecommit msg rejected your commit message")
  	    log.write("(message must follow format: 'topic: explanation')")
  	    return False
  
  runhooks('commit-msg', hooks=[validatecommitmsg])  
  ```

Example 5: validate unit test passing before commiting
-

The following hooks checks on the client side that the commit about to be made passes all unit tests.
I have it enabled for this repo to make sure that I respect the format I intended to keep.
Save the following file under .git/hooks/pre-commit and make it executable to test it:
 
  ```python
  from hooklib import basehook, runhooks 
  import os
  import subprocess
  
  class validateunittestpass(basehook): 
       def check(self, log, revdata): 
          testrun = "python %s/hooktests.py" % revdata.reporoot
          ret = subprocess.call(testrun, 
                                shell=True,
                                env={"PYTHONPATH":revdata.reporoot})
          if ret == 0:
              return True
          else:
              log.write("unit test failed, please check them")
              return False
  
  runhooks('pre-commit', hooks=[validateunittestpass])  
  ```

Installation
-
```
git clone https://github.com/charignon/hooklib.git
sudo python setup.py install
sudo pip install mercurial
```

Contributing
-
Before sending a Pull-Request please run the tests:

- To run the unit tests, simply call `python hooktests.py`, let's keep the unit test suite running under 1s
- To run the integration tests, download run-tests.py from the mercurial repo "https://selenic.com/hg/file/tip/tests/run-tests.py"
Then you can run the tests with `python run-tests.py test-git.t -l` (I only have tests for git so far)


