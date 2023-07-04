import logging
import os
from fastapi import FastAPI

from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.agent import AzureOpenAIConfig
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.synthesizer.azure_synthesizer import AzureSynthesizer
from vocode.streaming.transcriber.azure_transcriber import AzureTranscriber
from vocode.streaming.transcriber.azure_transcriber import AzureTranscriberConfig
from vocode.streaming.client_backend.conversation import ConversationRouter
from vocode.streaming.models.message import BaseMessage

# customized AzureChatGPTAgent
from azure_gpt_agent import AzureChatGPTAgent


from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url=None)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create conversation router
conversation_router = ConversationRouter(
    # create agent
    agent=AzureChatGPTAgent(
        ChatGPTAgentConfig(
            prompt_preamble="This is HSBC Hongkong customer service chatbot.",
            initial_message=BaseMessage(text=os.getenv("SPEECH_WELCOME_MESSAGE")),
            azure_params=AzureOpenAIConfig(
                api_type=os.getenv("AZURE_OPENAI_API_TYPE"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                engine=os.getenv("AZURE_OPENAI_API_ENGINE"),
            ),
        )
    ),
    # create transcriber for STT
    transcriber_thunk=lambda input_audio_config: AzureTranscriber(
        AzureTranscriberConfig.from_input_audio_config(
            input_audio_config=input_audio_config
        )
    ),
    # create synthesizer for TTS
    synthesizer_thunk=lambda output_audio_config: AzureSynthesizer(
        AzureSynthesizerConfig.from_output_audio_config(
            output_audio_config, voice_name=os.getenv("AZURE_SPEECH_VOICE_NAME")
        )
    ),
    logger=logger,
)

app.include_router(conversation_router.get_router())
