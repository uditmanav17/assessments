# Backend API

- Backend prediction service built in FastAPI

## Requirements
- Docker

## How to use?

Preferred way is to use `Docker Compose` present in root directory of repo.

In case, you want to spin up backend container independently, follow along -

- Change to `/src/backend`
- Build docker image using
```
docker build -t backend .
```
Above command will build a docker image named `backend`
- Spin up container using
```
docker run -p 1234:8000 --name backend --net=bridge -t backend
```
This will spin up a container with backend endpoints available at localhost:1234

Enjoy playing around!
