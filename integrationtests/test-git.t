Write a basic git update hook that authorizes only pushing to master
  $ mkdir server
  $ cd server
  $ serverpath=$(pwd)
  $ git init --bare .
  Initialized empty Git repository in $TESTTMP/server/

  $ cat <<EOF >> hooks/update
  > #!/usr/bin/python
  > from hooklib import basehook, runhooks
  > ERROR_MSG = "you can only push master on this repo"
  > class mastergatinghook(basehook):
  >     def check(self, log, revdata):
  >         check = revdata.refname == 'refs/heads/master'
  >         if not check:
  >             log.write(ERROR_MSG)
  >         return check
  > 
  > runhooks('update', hooks=[mastergatinghook])
  > EOF

  $ chmod +x hooks/update
  $ cd ..
  $ git init client
  Initialized empty Git repository in $TESTTMP/client/.git/
  $ cd client
  $ clientpath=$(pwd)
  $ git remote add origin file:///$serverpath
  $ echo "a" > a
  $ git add a
  $ git commit -am "Adding a" &> /dev/null
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
  > from hooklib import basehook, runhooks
  > class printinghook(basehook):
  >     def check(self, log, revdata):
  >         log.write("New ref: "+'\,'.join(revdata.revs))
  >         return True
  > 
  > runhooks('post-update', hooks=[printinghook])
  > EOF
  $ chmod +x ../server/hooks/post-update
  $ echo "x" > a
  $ git add a
  $ git commit -am "Adding x" &> /dev/null

  $ git push origin master
  remote: New ref: refs/heads/master        
  To file:///$TESTTMP/server
     *..*  master -> master (glob)

Parallel hook execution
  $ cat <<EOF >> ../server/hooks/post-update
  > #!/usr/bin/python
  > from hooklib import basehook, runhooks
  > import time
  > class slowhook(basehook):
  >     def check(self, log, revdata):
  >         time.sleep(0.1)
  >         return True
  > 
  > runhooks('post-update', hooks=[slowhook]*200, parallel=True)
  > EOF
  $ chmod +x ../server/hooks/post-update
  $ echo "y" > a
  $ git add a
  $ git commit -am "Adding y" &> /dev/null

  $ git push origin master
  remote: New ref: refs/heads/master        
  To file:///$TESTTMP/server
     *..*  master -> master (glob)
 
A hook to check that each commit message contains a message

  $ cat <<EOF >> ../server/hooks/update
  > #!/usr/bin/python
  > from hooklib import basehook, runhooks
  > ERROR_MSG = "you can only push commit with 'secretmessage' in the description"
  > class messagegatinghook(basehook):
  >     def check(self, log, revdata):
  >         for rev in revdata.revs:
  >             if not 'secretmessage' in revdata.commitmessagefor(rev):
  >                 log.write(ERROR_MSG)
  >                 return False
  >         return True
  > 
  > runhooks('update', hooks=[messagegatinghook])
  > EOF
  $ echo "z" > a
  $ git add a
  $ git commit -am "Hello world" &> /dev/null

  $ git push origin master
  remote: you can only push commit with 'secretmessage' in the description        
  remote: error: hook declined to update refs/heads/master        
  To file:///$TESTTMP/server
   ! [remote rejected] master -> master (hook declined)
  error: failed to push some refs to 'file:///$TESTTMP/server'
  [1]
  $ git commit --amend -m "Hello secretmessage world" &>/dev/null
  $ git push origin master
  remote: New ref: refs/heads/master        
  To file:///$TESTTMP/server
     *..*  master -> master (glob)

All the hooks!
  $ for hook in "applypatch-msg" "pre-applypatch" "post-applypatch" "pre-commit"  "prepare-commit-msg"  "commit-msg" "post-commit"  "pre-rebase"  "pre-push"  "pre-receive" "update"  "post-receive"  "post-update"; do 
  >     for side in "server" "client"; do
  >         if [[ $side == "server" ]]; then
  >             hpath="$serverpath/hooks/$hook"
  >         else
  >             hpath="$clientpath/.git/hooks/$hook"
  >         fi;
  >         rm -f $hpath
  >         mkdir -p $(dirname $hpath)
  >         echo "#!/usr/bin/python" >> $hpath
  >         echo "from hooklib import basehook, runhooks" >> $hpath
  >         echo "class loghook(basehook):" >> $hpath
  >         echo "    def check(self, log, revdata):" >> $hpath
  >         echo "        with open('$serverpath/res','a') as k:" >> $hpath
  >         echo "           k.write('$side: $hook\\\n')"      >> $hpath
  >         echo "        return True" >> $hpath
  >         echo "runhooks('$hook', hooks=[loghook])" >> $hpath
  >         chmod +x $hpath
  >     done;
  > done;
  $ echo "u" > a
  $ git add a
  $ echo "op: before first commit" >> $serverpath/res
  $ git commit -am "Hello world" &> /dev/null
  $ echo "op: after first commit" >> $serverpath/res
  $ echo "t" > b
  $ git add b
  $ echo "op: before second commit" >> $serverpath/res
  $ git commit -a --amend &>/dev/null
  [1]
  $ echo "op: after second commit" >> $serverpath/res
  $ echo "op: before push" >> $serverpath/res
  $ git push origin master
  To file:///$TESTTMP/server
     *..*  master -> master (glob)
  $ echo "op: after push" >> $serverpath/res
  $ cat $serverpath/res
  op: before first commit
  client: pre-commit
  client: prepare-commit-msg
  client: commit-msg
  client: post-commit
  op: after first commit
  op: before second commit
  client: pre-commit
  client: prepare-commit-msg
  op: after second commit
  op: before push
  client: pre-push
  server: pre-receive
  server: update
  server: post-receive
  server: post-update
  op: after push

