#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker system prune -a -f --volumes
cd metapub/metapub
sudo docker-compose up -d
cd ../../arxiv/arxiv
sudo docker-compose up -d
cd ../../core/core
sudo docker-compose up -d
cd ../../preprocessing/preprocessing
sudo docker-compose up -d
cd ../../db/db
sudo docker-compose up -d
cd ../../orchestrator/orchestrator
sudo docker-compose up -d
cd ../../gui/gui
sudo docker-compose up -d
