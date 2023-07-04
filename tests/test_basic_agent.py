import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

from customized_tools import refinitiv_freetext_news_summary_tool
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType

from langchain.chat_models import AzureChatOpenAI


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
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=7_000, chunk_overlap=400)


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
