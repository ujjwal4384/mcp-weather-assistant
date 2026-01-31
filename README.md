# Weather Assistant

This project is a conversational AI agent that provides real-time weather information for any location. The agent is built using LangGraph and powered by Google's Gemini 2.5 Flash model, and it interacts with a custom-built server to fetch weather data from the OpenWeatherMap API.

## Features

- **Conversational Interface:** Interact with the agent in a natural, conversational way.
- **Real-time Weather Data:** Get up-to-date weather information for any city in the world.
- **Client-Server Architecture:** The project is modular, with a clear separation between the conversational agent (client) and the data-fetching service (server).
- **Powered by LangGraph and Gemini:** The agent uses LangGraph for state management and is powered by the advanced Gemini 2.5 Flash large language model.

## Architecture

The Weather Assistant uses a client-server architecture:

- **Client (`client/main.py`):** The client is a command-line interface that allows you to chat with the weather agent. It is built with:
  - `langchain` and `langgraph` to create and manage the conversational agent's logic.
  - `mcp` to facilitate communication with the server.
  - `langchain_google_genai` to integrate with the Gemini 2.5 Flash model.
  
- **Server (`server/weather-server.py`):** The server exposes a tool that the agent can use to fetch weather information. It is built with:
  - `FastMCP` to create a lightweight and efficient server.
  - `requests` to make API calls to the OpenWeatherMap service.
  - `python-dotenv` to manage environment variables.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- An API key from [OpenWeatherMap](https://openweathermap.org/api)
- A `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/weather-assistant.git
   cd weather-assistant
   ```

2. **Install the dependencies for both the client and the server:**
   ```bash
   pip install -r requirements.txt
   pip install -r server/requirements.txt
   ```

3. **Set up your environment variables:**
   Create a `.env` file inside the `server` directory and add your API keys:
   ```
   OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
   GEMINI_API_KEY="your_gemini_api_key"
   ```

### Usage

To start the Weather Assistant, run the `main.py` file in the `client` directory:

```bash
python client/main.py
```

The application will start, and you can begin asking for the weather. Here are a few examples:

```
You: What's the weather in London?
AI: The weather in London is currently overcast clouds with a temperature of 12.3°C...

You: How about in Tokyo?
AI: In Tokyo, the weather is clear sky, with a temperature of 22.5°C...
```

To exit the application, type `exit`, `quit`, or `q`.

## How It Works

1. The client-side application, built with `langgraph`, manages the conversation flow.
2. When you ask for the weather in a specific location, the agent identifies the required tool (`get_weather`) and the location entity.
3. The client sends a request to the server using the `mcp` protocol, invoking the `get_weather` tool with the specified location.
4. The server-side tool fetches the weather data from the OpenWeatherMap API.
5. The weather information is sent back to the client, which then presents it to you in a human-readable format.

## Dependencies

### Client

- `langchain`: For building the conversational agent.
- `langgraph`: To manage the agent's state and conversation flow.
- `langchain-google-genai`: To integrate with the Gemini 2.5 Flash model.
- `python-dotenv`: For managing environment variables.
- `mcp`: For communication between the client and the server.

### Server

- `FastMCP`: To create the server and expose the weather tool.
- `requests`: To fetch data from the OpenWeatherMap API.
- `python-dotenv`: For managing environment variables.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.