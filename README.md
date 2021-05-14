# Media Moderator

This project uses machine learning to to determine if a file contains anything NSFW. 

NOTE: This repository DOES NOT contain any NSFW content, besides some language used as categorization for the model.

## Requirements

This project uses Docker to build and run each service.

- [Docker](https://docs.docker.com/get-docker/)

### Requirements for Building Services Without Docker

Each service can also be run individually, but have the following requirements respectively:

- [PostgreSQL](https://www.postgresql.org/download/)
- [Node.js](https://nodejs.org/en/)
- [Python3](https://www.python.org/downloads/)
- [Django](https://www.djangoproject.com/download/)
- [NGINX](https://www.nginx.com/)

### Environment Files

To use this project with Docker, you'll need to create your own .env files. On the same level as this README, create a .env file with the following definitions:

```bash
ENV_API_SERVER=[Domain name or http://127.0.0.1]
```

For instructions on a service's .env file requirements, see the service-level README.md.

## Usage

Docker is used to run each service in parallel. After cloning the repository and navigating to the project's root, run the following command:

```bash
docker-compose up -d
```

Then, navigate to 127.0.0.1 to see the home page. The URL to the prediction API is 127.0.0.1/api/predict/. I use [Postman](https://www.postman.com/) to do local API testing.

To shutdown the Docker network, run the following command:

```bash
docker-compose down
```

If you would like to rebuild a single service in the network, run the following command:

```bash
docker-compose build [SERVICE]
docker-compose up -d
```

NOTE: Rebuilding the React app after creating the services using Docker compose can cause the page to display a white screen. This is due to the Nginx web server and the React app having a shared static volume that doesn't get updated on rebuild, and can be remedied with the following command:

```bash
docker volume rm mp4-content-moderator_react_static_volume
```

If that doesn't work, you can wipe all volumes:

```bash
docker volume rm $(docker volume ls -q)
```

See [docker-compose documentation for more information.](https://docs.docker.com/compose/)
