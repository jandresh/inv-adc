#! /bin/bash
sudo rm -fr inv-adc
git clone https://github.com/jandresh/inv-adc
cd inv-adc/
for branch in `git branch -r | grep -v HEAD`;do echo -e `git show --format="%ci" $branch | head -n 1` \\t$branch; done | sort -r | head -n 1 | grep -o -P '(?<=origin/).*(?=)' > branch.txt
export LAST_BRANCH=$(cat branch.txt)
git checkout $LAST_BRANCH
cd orchestrator/kompose
sudo docker-compose down --remove-orphans
cd ../../db/kompose
sudo docker-compose down --remove-orphans
cd ../../preprocessing/kompose
sudo docker-compose down --remove-orphans
cd ../../core/kompose
sudo docker-compose down --remove-orphans
cd ../../arxiv/kompose
sudo docker-compose down --remove-orphans
cd ../../metapub/kompose
sudo docker-compose down --remove-orphans
cd ..
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
