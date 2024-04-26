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

COPY ./ /app
WORKDIR /app

EXPOSE 8000

# --reload not to be used in prod env
# use gunicorn to run application - https://fastapi.tiangolo.com/deployment/server-workers/
CMD ["uvicorn", "api_backend:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
