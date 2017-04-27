FROM node:7.8-alpine

RUN npm install --global --no-optional --quiet redis-commander@~0.4.2

EXPOSE 8081
ENTRYPOINT ["redis-commander"]