# Kopi Debate Chatbot

A conversational chatbot designed to engage in debates on various
controversial topics, adopting a stance and defending it with arguments.

------------------------------------------------------------------------

## OVERVIEW

This service exposes a REST API to interact with the chatbot. You can
start a new conversation or continue an existing one. The bot will
detect the conversation's topic and oppose the user's position to 
encourage debate.

The project is containerized with Docker and designed for easy setup and
deployment, connecting to the OpenAI API for its generative
capabilities.

------------------------------------------------------------------------

## ARCHITECTURE

The project is structured following the principles of Hexagonal
Architecture (Ports and Adapters). This separates the core business
logic (the domain) from external implementation details.

-   **Domain** (`src/chatbot/domain`): Contains the pure chatbot logic,
    with no dependencies on external frameworks.
-   **Adapters** (`src/chatbot/adapters`): Connect the domain to the
    outside world.
    -   **API**: The input adapter that exposes HTTP endpoints using
        FastAPI.
    -   **Storage**: The output adapter that implements conversation
        persistence (currently in-memory).
    -   **LLM**: The output adapter that communicates with the
        generative AI provider (currently OpenAI).

This design makes the system highly modular and easy to test, maintain,
and extend.

------------------------------------------------------------------------

## PREREQUISITES

To run this project, you will need:

-   Docker and `docker-compose`.
-   An OpenAI API Key.

------------------------------------------------------------------------

## SETUP

1.  Clone the repository:

    ``` bash
    git clone https://github.com/UlisesMiranda/Kopi-challengue.git
    cd Chatbot
    ```

2.  Create the environment file:\
    This project requires an OpenAI API Key. Create a file named `.env`
    in the root of the project and add your key:

    ``` env
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

    > Note: The `.env` file is included in `.gitignore` to prevent
     accidentally committing your secret key.

------------------------------------------------------------------------

## USAGE

Running the Service:\
To start the chatbot API, simply run:

``` bash
make run
```

This command will build the Docker image if it doesn't exist and then
start the service.\
The service will be available at `http://localhost:8000`.\
You can stop it at any time by pressing `Ctrl+C`.

Once running, you can access the interactive API documentation (Swagger
UI) at:\
`http://localhost:8000/docs`

Running Tests:
To run the complete test suite (make sure you have run `make install` first):
``` bash
make test
```

------------------------------------------------------------------------

## API DOCUMENTATION

### POST /chat

The main endpoint to interact with the chatbot.

**Request Body:**

``` json
{
  "conversation_id": "string (optional)",
  "message": "string (required)"
}
```

-   `conversation_id`: If omitted or null, a new conversation will be
    started.\
-   `message`: The user's message for the chatbot.

**Success Response (200 OK):**

``` json
{
  "conversation_id": "string",
  "message": [
    {
      "role": "user",
      "message": "The user's message"
    },
    {
      "role": "bot",
      "message": "The bot's response"
    }
  ]
}
```

------------------------------------------------------------------------

### GET /health

A simple endpoint to verify that the service is running.

**Success Response (200 OK):**

``` json
{
  "status": "healthy",
  "timestamp": "2024-09-05T12:00:00.000000"
}
```

------------------------------------------------------------------------

## EXAMPLE REQUEST

1. Start a new conversation using curl:

``` bash
curl -X POST "http://localhost:8000/chat"      -H "Content-Type: application/json"      -d '{
       "message": "I think the moon landing was real"
     }'
```

The response will include a `conversation_id`.

2. Continue an existing conversation:
   Use the `conversation_id` from the previous response to continue the debate.

``` bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/json" \
        -d '{
          "conversation_id": "<conversation_id>",
          "message": "But there is solid evidence about the trip"
        }'
```

------------------------------------------------------------------------

## MAKEFILE COMMANDS

This project uses a Makefile to simplify common tasks. You can see all
available commands by running:

``` bash
make
```

**Available Commands:**

-   `help` -\> Shows the list of available commands.\
-   `install` -\> Builds the Docker images for production and testing.\
-   `test` -\> Runs all tests inside a Docker container.\
-   `run` -\> Runs the chatbot service.\
-   `down` -\> Stops the running service container.\
-   `clean` -\> Stops and removes the service container and associated
    volumes.
