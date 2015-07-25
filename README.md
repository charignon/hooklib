# hooklib: write source control hooks in Python

Python hook helper library:
- SCM Agnostic: Can work with different SCM (git, svn, hg), write your hook once and they work on other SCMs
- Simple API: Don't learn the secret commands to peek inside your source control system, all you need is accessible and computed on the fly
- Parallel/Sequential mode: Run your hooks in parallel or sequentially

Currently only supports git.


Example 1: gate commit on commit message format
-

Save the following file under .git/hooks/update and make it executable to test it: 
```python
#!/usr/bin/python
from hooklib import basehook, runhooks
ERROR_MSG = "you can only push commit with 'secretmessage' in the description"
class commmitmsggatinghook(basehook):
   def check(self, log, revdata):
       for rev in revdata.revs:
           if not 'secretmessage' in revdata.commitmessagefor(rev):
               log.write(ERROR_MSG)
               return False
       return True

runhooks('update', hooks=[commmitmsggatinghook])
```

Example 2: only authorize push to master
-

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

Contributing
-
Before sending a Pull-Request please run the tests:

- To run the unit tests, simply call `python hooktests.py`, let's keep the unit test suite running under 1s
- To run the integration tests, download run-tests.py from the mercurial repo "https://selenic.com/hg/file/tip/tests/run-tests.py"
Then you can run the tests with `python run-tests.py test-git.t -l` (I only have tests for git so far)


