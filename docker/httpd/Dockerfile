FROM httpd:2.4
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf

# 환경 변수 설정
ARG REPO_URL=http://github.com/DONGUK777/DONGUK777.github.io.git
# ARG BRANCH_NAME=240829/firebase

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]
RUN ["apt-get", "install", "-y", "git"]
#RUN ["git", "clone", "git@github.com:DONGUK777/DONGUK777.github.io.git", "/usr/local/apache2/blog"]
RUN git clone -b 240829/firebase ${REPO_URL} /usr/local/apache2/myblog
# docker run option??


