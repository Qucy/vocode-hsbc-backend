import os
import logging
from typing import AsyncGenerator, Optional, Tuple
from vocode.streaming.agent.base_agent import RespondAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from langchain.chat_models import AzureChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory

from customized_tools import hsbc_knowledge_tool, reject_tool

# prompt prefix append before the chat conversation
PROMPT_PREFIX = """
You are a customer service AI for HSBC Hongkong, your primary focus would be to assist customers with questions and issues related to HSBC Hongkong products and services. 
If a customer asks a question that is not related to HSBC Hongkong, politely inform them that I am only able to assist with HSBC Hongkong related questions.

You have access to the following tools:
"""

class AzureChatGPTAgent(RespondAgent[ChatGPTAgentConfig]):
    
    def __init__(
        self,
        agent_config: ChatGPTAgentConfig,
        logger: Optional[logging.Logger] = None,
        openai_api_key: Optional[str] = None,
    ):
        # init base agent
        super().__init__(agent_config=agent_config, logger=logger)

        # check if azure params are set
        if not agent_config.azure_params:
            raise ValueError("AzureOpenAIConfig must be set in agent config")
        
        # set up azure openai api
        os.environ['OPENAI_API_KEY'] = os.getenv('AZURE_OPENAI_API_KEY')
        os.environ["OPENAI_API_BASE"] = os.getenv('AZURE_OPENAI_API_BASE')
        os.environ["OPENAI_API_TYPE"] = os.getenv('AZURE_OPENAI_API_TYPE')
        os.environ["OPENAI_API_VERSION"] = os.getenv('AZURE_OPENAI_API_VERSION')

        # create llm model
        self.llm = AzureChatOpenAI(deployment_name=os.getenv('AZURE_OPENAI_API_ENGINE'))

        # create tools
        self.tools = [hsbc_knowledge_tool, reject_tool]

        # create memory, window size = 10
        self.memory = ConversationBufferWindowMemory(k=10)

        # create agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )

    async def generate_response(
        self,
        human_input: str,
        conversation_id: str,
        is_interrupt: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        Generate a response to a human input
        """
        # check if interrupt
        if is_interrupt and self.agent_config.cut_off_response:
            cut_off_response = self.get_cut_off_response()
            yield cut_off_response
            return
        # check if transcript is set
        assert self.transcript is not None
        # get response from llm
        response = self.agent.run(input=human_input)
        # split by space TODO replace by streaming api later
        messages = response.split(" ")
        # return generator
        for message in messages:
            yield message

    
    async def respond(
        self,
        human_input,
        conversation_id: str,
        is_interrupt: bool = False,
    ) -> Tuple[str, bool]:
        raise NotImplementedError

