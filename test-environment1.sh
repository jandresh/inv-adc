#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker system prune -a -f --volumes
cd metapub
sudo docker-compose build
sudo docker-compose up -d
cd ../arxiv
sudo docker-compose build
sudo docker-compose up -d
cd ../core
sudo docker-compose build
sudo docker-compose up -d
cd ../preprocessing
sudo docker-compose build
sudo docker-compose up -d
cd ../db
sudo docker-compose build
sudo docker-compose up -d
cd ../orchestrator
sudo docker-compose build
sudo docker-compose up -d
cd ../gui
sudo docker-compose build
sudo docker-compose up -d
