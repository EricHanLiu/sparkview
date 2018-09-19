FROM python:3.6.5


ENV PROJECT_DIR "/bloom"
RUN mkdir -p $PROJECT_DIR
WORKDIR $PROJECT_DIR
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt





