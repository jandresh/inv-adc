FROM node:current

WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install

RUN npm install -g serve

COPY . .

EXPOSE 3000

CMD [ "serve", "-s", "build" ]
