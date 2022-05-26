#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout development
git merge $LAST_BRANCH
git branch -d $LAST_BRANCH
# git push
