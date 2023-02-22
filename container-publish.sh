#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
sudo docker login -u="jandresh" -p="cb64422a-f28c-4ee7-b717-f605e309a1b2"
cd metapub/app
sudo docker build -t jandresh/metapub:$GIT_COMMIT .
sudo docker push jandresh/metapub:$GIT_COMMIT
sudo docker build -t jandresh/metapub:latest .
sudo docker push jandresh/metapub:latest
cd ../arxiv/app
sudo docker build -t jandresh/arxiv:$GIT_COMMIT .
sudo docker push jandresh/arxiv:$GIT_COMMIT
sudo docker build -t jandresh/arxiv:latest .
sudo docker push jandresh/arxiv:latest
cd ../../core/app
sudo docker build -t jandresh/core:$GIT_COMMIT .
sudo docker push jandresh/core:$GIT_COMMIT
sudo docker build -t jandresh/core:latest .
sudo docker push jandresh/core:latest
cd ../../preprocessing/app
sudo docker build -t jandresh/preprocessing:$GIT_COMMIT .
sudo docker push jandresh/preprocessing:$GIT_COMMIT
sudo docker build -t jandresh/preprocessing:latest .
sudo docker push jandresh/preprocessing:latest
cd ../../db/app
sudo docker build -t jandresh/db:$GIT_COMMIT .
sudo docker push jandresh/db:$GIT_COMMIT
sudo docker build -t jandresh/db:latest .
sudo docker push jandresh/db:latest
cd ../../orchestrator/app
sudo docker build -t jandresh/orchestrator:$GIT_COMMIT .
sudo docker push jandresh/orchestrator:$GIT_COMMIT
sudo docker build -t jandresh/orchestrator:latest .
sudo docker push jandresh/orchestrator:latest
cd ../../gui/
sudo docker build -t jandresh/gui:$GIT_COMMIT .
sudo docker push jandresh/gui:$GIT_COMMIT
sudo docker build -t jandresh/gui:latest .
sudo docker push jandresh/gui:latest
