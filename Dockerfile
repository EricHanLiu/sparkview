FROM python:3.6.5


ENV PROJECT_DIR "/bloom"
ENV APP_NAME "bloom"
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


RUN ["chmod", "+x", ".deploy/docker-entrypoint.sh"]

