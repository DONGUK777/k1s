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


