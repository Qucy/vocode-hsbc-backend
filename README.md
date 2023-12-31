# Project Name

This is a Python-based backend project that provides an all-in-one chat experience using the Vocode and Langchain libraries. The goal of the project is to enable users to interact with a large language model using speech-to-text and text-to-speech services. The application allows users to input spoken text, which is then processed by the language model to generate a response. The project is designed to be based on our PoC requirments.

## Getting Started

### Prerequisites

- Python 3.9 or higher is required to run the application, with Python 3.11 recommended.
- The main libraries used in the application are Vocode for speech-to-text and text-to-speech conversion and Langchain for communication between the language model service and the application.
- In addition to the libraries, you will need a valid large language model service such as OpenAI or Azure OpenAI to use the application.
- You will also need a valid speech service such as Azure Speech Service, Google Speech Service, or Deepgram Speech Service to enable speech-to-text conversion.

Please ensure that you have installed all necessary libraries and have valid credentials for the language and speech services before running the application. Additional setup steps may be required depending on your specific use case.

### Installing

To install the required libraries for the application, run the following command:

```bash
pip install -r requirements.txt
```

This will install all the necessary libraries listed in the requirements.txt file.

Finally manually install langchain via below command, the current langchain installed via vocodo liberary is out of date. And ignore the warning message (vocode 0.1.110 requires langchain<0.0.150,>=0.0.149)
```bash
pip install langchain==0.0.216
```

### Running the Application

To start the application, run the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

This will start the application on port 8000 and make it accessible from any IP address.

## Usage

To use this application, you will need to combine it with the frontend project vocode-hsbc-frontend. You will need to set the conversation endpoint in the frontend project, for example ws://localhost:8000. This will allow the frontend to call the API at the backend and enable users to communicate with the language model and speech services.

Once the backend and frontend are connected, the user can input spoken or written text, which will be processed by the language model to generate a response. The response can then be converted to speech using the text-to-speech service and played back to the user.

## Configuration

To configure the application, create a .env file in the root directory of the project and set the following environment variables:

```.env
AZURE_OPENAI_API_TYPE=[your API type]
AZURE_OPENAI_API_KEY=[your API key]
AZURE_OPENAI_API_BASE=[your Azure API endpoint]
AZURE_OPENAI_API_VERSION=[your Azure API version]
AZURE_OPENAI_API_ENGINE=[your Azure API engine]
AZURE_OPENAI_API_MODEL=[your Azure Model name]
AZURE_SPEECH_KEY=[your Azure Speech key]
AZURE_SPEECH_REGION=[your Azure Speech region]
AZURE_SPEECH_VOICE_NAME=[your Azure TTS voice]
SPEECH_WELCOME_MESSAGE=[your welcome message]
```

Please replace the values in square brackets with your own values for the respective services and settings. These environment variables are used to configure the language and speech services used by the application, as well as to set other application settings such as the welcome message.

## Airflow job

In this project, Airflow is used to scrape knowledge information from the HSBC website. The knowledge information is scraped on a daily basis and stored in a database.

The Airflow job is configured and running on GCP MapleQuad. The console address for the Airflow job is https://t6dc1abd119b5dff1p-tp.appspot.com/home.

## Deployment

The backend and frontend have been successfully deployed to MapleQuad GCP, along with all the required libraries including Python 3.11, Node v18, and React.js. Therefore, redeploying the code is a matter of stopping the current service, removing the current source code folder for the backend or frontend, cloning the new code, and restarting the service.

The backend code is located in the following path: /root/vocode-hsbc-backend
The frontend code is located in the following path: /root/vocode-hsbc-frontend
The venv Python environment has been created at: /root/vocode_python_env

To start or stop the application, navigate to the project root folder and use the provided start.sh and stop.sh scripts. Remember to run chmod +x *sh to make the scripts executable before running them.


## Contributing

- Qucy/Steven for backend and LLM agents
- Qucy/Nicolas for frontend UI

### TODOs

- UI enhancemeant, display script at left side of screen and display button at right side of screen
- knowledge query tool hsbc.hk.com (Qucy)
- news query (Steven)
- PDF/OCR Document Search (Steven)
- Financial Market Index Data Query (Steven/Tom/Qucy) Quandl API

## License

Not applicable.
