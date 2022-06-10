#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
cd gui
sudo docker-compose down --remove-orphans
cd ../orchestrator
sudo docker-compose down --remove-orphans
cd ../db
sudo docker-compose down --remove-orphans
cd ../preprocessing
sudo docker-compose down --remove-orphans
cd ../core
sudo docker-compose down --remove-orphans
cd ../arxiv
sudo docker-compose down --remove-orphans
cd ../metapub
sudo docker-compose down --remove-orphans
cd kompose
sudo docker-compose up -d
cd ../../arxiv/kompose
sudo docker-compose up -d
cd ../../core/kompose
sudo docker-compose up -d
cd ../../preprocessing/kompose
sudo docker-compose up -d
cd ../../db/kompose
sudo docker-compose up -d
cd ../../orchestrator/kompose
sudo docker-compose up -d
cd ../../gui/kompose
sudo docker-compose up -d
