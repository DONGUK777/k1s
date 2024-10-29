# K1S
- https://hub.docker.com/_/httpd

# BUILD & RUN
```bash

# BUILD
$ $ docker build -t my-apache2 .

# RUN
# $ docker run -dit --name my-running-app -p 8949:80 my-apache2
# $ docker run -dit --name my-running-app -p 8949:80 -v "$PWD":/usr/local/apache2/blog/:ro --rm my-apache2 # 도커에게 read only 권한만 부여
$ docker run -dit --name my-running-app -p 8949:80 -v "$PWD":/usr/local/apache2/blog/ my-apache2

# CONTAINER
$ docker exec -it my-running-app bash
```

# LB
```bash
$ docker build -t blog docker/httpd
$ docker run -d --name blog-1 --rm blog
$ docker build -t lb docker/nginx
$ docker run -d --name ngix_lb -p 8949:80 --link blog-1 --rm lb
```

# COMPOSE
- https://docs.docker.com/reference/cli/docker/compose/up/
- https://docs.docker.com/compose/how-tos/file-watch/

```bash
$ docker compose -f docker-compose.yaml up -d 
$ docker compose up -d 
$ docker compose up -d --build
$ docker compose up -d --build --force-recreate
$ docker compose up -d --scale blog=1
$ docker compose up -d --scale blog=2
$ docker compose up -d --watch

$ docker compose stop
$ docker compose start
$ docker compose down
```
