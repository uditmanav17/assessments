# FROM huggingface/transformers-pytorch-cpu:latest
FROM python:slim

# don't save caches
ENV PIP_NO_CACHE_DIR=1
# avoid .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# stream outputs to logs
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8080

# change streamlit server config in prod
ENTRYPOINT ["streamlit","run"]

CMD ["streamlit_frontend.py", "--server.port", "8080"]
