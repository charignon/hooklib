Write a basic hg update hook that gates push on condition on commit message
  $ mkdir server
  $ cd server
  $ serverpath=$(pwd)
  $ hg init
  $ mkdir .hg/hooks
  $ cat <<EOF >> .hg/hooks/update
  > #!/usr/bin/python
  > from hooklib import basehook, runhooks
  > 
  > class commmitmsggatinghook(basehook):
  >    def check(self, log, revdata):
  >        for rev in revdata.revs:
  >            if not 'secretmessage' in revdata.commitmessagefor(rev):
  >                log.write("commit message must contain 'secretmessage'")
  >                return False
  >        return True
  > 
  > runhooks('update', hooks=[commmitmsggatinghook])
  > EOF

  $ cat <<EOF >>$HGRCPATH
  > [hooks]
  > EOF
  $ echo "commit=${serverpath}/.hg/hooks/update" >> $HGRCPATH

  $ chmod +x .hg/hooks/update
  $ cd ..
  $ hg init client
  $ cd client
  $ echo "a" > a
  $ hg add a
  $ hg commit -m "Adding a"
  commit message must contain 'secretmessage'
  warning: commit hook exited with status 1
  $ hg push -r. file://${serverpath}
  pushing to file://$TESTTMP/server
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 1 changesets with 1 changes to 1 files
