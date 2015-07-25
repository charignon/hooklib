Write a basic git update hook that authorizes only pushing to master
  $ mkdir server
  $ cd server
  $ serverpath=$(pwd)
  $ git init --bare .
  Initialized empty Git repository in $TESTTMP/server/

  $ cat <<EOF >> hooks/update
  > #!/usr/bin/python
  > from hooklib import basehook, hookrunner
  > ERROR_MSG = "you can only push master on this repo"
  > class failinghook(basehook):
  >     def check(self, log, revdata):
  >         check = revdata['name'] == 'refs/heads/master'
  >         if not check:
  >             log.write(ERROR_MSG)
  >         return check
  > 
  > hookrunner.run('update', failinghook)
  > EOF

  $ chmod +x hooks/update
  $ cd ..
  $ git init client
  Initialized empty Git repository in $TESTTMP/client/.git/
  $ cd client
  $ git remote add origin file:///$serverpath
  $ echo "a" > a
  $ git add a
  $ git commit -am "Adding a"
  [master (root-commit) *] Adding a (glob)
   1 file changed, 1 insertion(+)
   create mode 100644 a
  $ git push origin master
  To file:///$TESTTMP/server
   * [new branch]      master -> master
  $ git push origin master:stable
  remote: you can only push master on this repo        
  remote: error: hook declined to update refs/heads/stable        
  To file:///$TESTTMP/server
   ! [remote rejected] master -> stable (hook declined)
  error: failed to push some refs to 'file:///$TESTTMP/server'
  [1]

Add a post-update hook that prints the refs that are pushed
  $ cat <<EOF >> ../server/hooks/post-update
  > #!/usr/bin/python
  > from hooklib import basehook, hookrunner
  > class failinghook(basehook):
  >     def check(self, log, revdata):
  >         log.write("New ref: "+'\,'.join(revdata['revs']))
  >         return True
  > 
  > hookrunner.run('post-update', failinghook)
  > EOF
  $ chmod +x ../server/hooks/post-update
  $ echo "x" > a
  $ git add a
  $ git commit -am "Adding x"
  [master *] Adding x (glob)
   1 file changed, 1 insertion(+), 1 deletion(-)
  $ git push origin master
  remote: New ref: refs/heads/master        
  To file:///$TESTTMP/server
     *..*  master -> master (glob)

