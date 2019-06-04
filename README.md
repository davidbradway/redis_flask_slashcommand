# Redis Flask for /remember slash command in Slack

```bash
docker-compose build
docker-compose up -d
docker exec -it redisflaskslashcommand_redis_1 redis-cli
```

```
ping
> PONG
set mykey somevalue
> OK
get mykey
> "somevalue"
exit
```

```bash
docker-compose down
docker container rm redisflaskslashcommand_redis_1
docker container rm redisflaskslashcommand_app_1

docker image ls
docker image rm redis:3.2-alpine
docker image rm python:3.6-alpine
```
