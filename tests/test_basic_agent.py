import os

from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chat_models import AzureChatOpenAI

from customized_tools import (
    document_question_answering,
    refinitiv_freetext_news_summary_tool,
)

# load environment variables
load_dotenv()

# set global variables
RKD_USERNAME = os.getenv("REFINITIV_USERNAME")
RKD_PASSWORD = os.getenv("REFINITIV_PASSWORD")
RKD_APP_ID = os.getenv("REFINITIV_APP_ID")

# text by an LLM, use temperature = 0.0
CHAT_LLM = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_API_ENGINE"), temperature=0
)


def test_basic_agent_news_search():
    """Test basic agent with news search tool."""

    # initialise tools
    tools = load_tools(["llm-math"], llm=CHAT_LLM)

    # initialise agent
    generic_agent = initialize_agent(
        tools + [refinitiv_freetext_news_summary_tool],
        CHAT_LLM,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True,
    )
    # print(generic_agent("What is 5+5?"))

    result = generic_agent("What is the latest news headline?")
    assert isinstance(result, dict)
    assert isinstance(result["input"], str)
    assert isinstance(result["output"], str)
    assert len(result["output"]) > 0

    print(result)


def test_basic_agent_docsearch():
    """Test basic agent with news search tool."""

    # initialise tools
    tools = load_tools(["llm-math"], llm=CHAT_LLM)

    # initialise agent
    generic_agent = initialize_agent(
        tools + [document_question_answering],
        CHAT_LLM,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        handle_parsing_errors=True,
        verbose=True,
    )
    # print(generic_agent("What is 5+5?"))

    result = generic_agent("what is HSBCs house view on investments?")
    assert isinstance(result, dict)
    assert isinstance(result["input"], str)
    assert isinstance(result["output"], str)
    assert len(result["output"]) > 0

    print(result)
