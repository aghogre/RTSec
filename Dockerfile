FROM mongo:3.2.10

#create DB directory
RUN mkdir -p /data/db

EXPOSE 27017

CMD ["mongod"]
