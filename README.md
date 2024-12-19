# Therapy Chatbot Backend v2

This guide will help you install and run the Therapy Chatbot Backend v2 on your local machine. Follow the steps below to get started.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. **Clone the Repository**

    Open a terminal and run the following command to clone the repository:

    ```sh
    git clone https://github.com/yourusername/therapist_chatbot.git
    cd therapist_chatbot/backend_v2
    ```

2. **Create Environment Variables File**

    Create a `.env` file in the `backend_v2` directory with the following content:

    ```env
    DATABASE_URL=postgresql://prodevkitty:prodevkitty827@postgres:5432/prodevDB
    REDIS_URL=redis://redis:6379/0
    CEREBRAS_API_KEY=csk-nvjvd3px8px3x855rymkp54mypv6fcw8n3vhn2nf8vf2xhr8
    ```

## Running the Application

1. **Start Docker Containers**

    Run the following command to start the Docker containers:

    ```sh
    docker-compose up
    ```

    This command will build and start the necessary containers for PostgreSQL, Redis, and the FastAPI application.

2. **Access the Application**

    Once the containers are up and running, you can access the application by navigating to `http://localhost:8001` in your web browser.

## Stopping the Application

To stop the application, press `Ctrl+C` in the terminal where you ran `docker-compose up`. Then, run the following command to stop and remove the containers:

```sh
docker-compose down
```

## Troubleshooting

If you encounter any issues, try the following steps:

- Ensure Docker and Docker Compose are installed and running.
- Check the terminal output for any error messages and address them accordingly.
- Verify that the `.env` file is correctly configured.

For further assistance, please refer to the [Docker documentation](https://docs.docker.com/get-started/) or contact the development team.
