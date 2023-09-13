Error git

`hint: Diverging branches can't be fast-forwarded, you need to either:
hint: 
hint:   git merge --no-ff
hint: 
hint: or:
hint: 
hint:   git rebase
hint: 
hint: Disable this message with "git config advice.diverging false"

hint: You have divergent branches and need to specify how to reconcile them.
hint: You can do so by running one of the following commands sometime before
hint: your next pull:
hint: 
hint:   git config pull.rebase false  # merge
hint:   git config pull.rebase true   # rebase
hint:   git config pull.ff only       # fast-forward only
hint: 
hint: You can replace "git config" with "git config --global" to set a default
hint: preference for all repositories. You can also pass --rebase, --no-rebase,
hint: or --ff-only on the command line to override the configured default per
hint: invocation.
fatal: Need to specify how to reconcile divergent branches.
`


# Solution
you can use
disable pull rebase by:

`git config pull.rebase false`

and change ff only to true

`git config pull.ff true`

you can merge tow branh ff overrive hash of commit branh(feature) merge to branh root (develop) other in pull request. if have change in develop repositry remote it have confict
