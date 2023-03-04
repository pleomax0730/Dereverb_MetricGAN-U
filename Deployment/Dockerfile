FROM python:3.8-slim-bullseye

ENV LANG C.UTF-8

RUN apt-get update && \
    apt-get install -y bash \
    build-essential \
    curl \
    libsndfile1-dev \
    ca-certificates 


RUN python -m pip install --no-cache-dir --upgrade pip


WORKDIR /home/ubuntu/Dereverb

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8864

COPY . .

CMD ["bash", "script.sh"]
