FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    gunicorn && \
    apt-get clean

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY html /app/html/
COPY static/story.js /app/static/
COPY server.py /app/
COPY create_audio.py /app/
COPY create_story.py /app/
COPY make_topics.py /app/
COPY stories.py /app/
COPY topics.py /app/
# COPY local_init.py /app/

WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "server:app"]