FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    gunicorn \
    python3-gdbm && \
    apt-get clean

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY html /app/html/
COPY static/story.js /app/static/
COPY server.py /app/
COPY audio.py /app/
COPY text.py /app/
COPY create_story.py /app/
COPY make_topics.py /app/
COPY stories.py /app/
COPY topics.py /app/

WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "server:app"]