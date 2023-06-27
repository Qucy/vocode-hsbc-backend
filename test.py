"""
This is a test class will not include in the final product
"""
import os
import re

from langchain.chat_models import AzureChatOpenAI
from langchain import LLMChain
from langchain.llms import AzureOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType, Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import BaseChatPromptTemplate
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage

from dotenv import load_dotenv

load_dotenv()

# set up azure openai api
os.environ['OPENAI_API_KEY'] = os.getenv('AZURE_OPENAI_API_KEY')
os.environ["OPENAI_API_BASE"] = os.getenv('AZURE_OPENAI_API_BASE')
os.environ["OPENAI_API_TYPE"] = os.getenv('AZURE_OPENAI_API_TYPE')
os.environ["OPENAI_API_VERSION"] = os.getenv('AZURE_OPENAI_API_VERSION')

# create llm models
llm_chat = AzureChatOpenAI(deployment_name=os.getenv('AZURE_OPENAI_API_ENGINE'), temperature=0)
llm_normal = AzureOpenAI(deployment_name=os.getenv('AZURE_OPENAI_API_ENGINE'), temperature=0)

def hsbc_knowledge_tool(input: str) -> str:
    return """
        Need to open a bank account with HSBC HK? You can apply with us if you:
        - are at least 18 years old
        - meet additional criteria depending on where you live
        - have proof of ID, proof of address

    If customer wants to apply online via mobile app:
        - They need to download the HSBC HK App to open an account online.
        - holding an eligible Hong Kong ID or an overseas passport
        - new to HSBC
    """

def news_query_tool(input: str) -> str:
    return """
        Here are the latest news:
        - 2021-11-01: HSBC Holdings plc 3Q 2021 Earnings Release
        - 2021-10-29: HSBC Holdings plc 3Q 2021 Earnings Release
        - 2021-10-29: HSBC Holdings plc 3Q 2021 Earnings Release
    """

## Tools need to include:

# know query tool hsbc.hk.com (Qucy)

# news query (Steven)

# PDF/OCR Document Search (Steven)

# Financial Market Index Data Query (Steven/Tom/Qucy) Quandl API

# Define which tools the agent can use to answer user queries
tools = [
    Tool(
        name = "hsbc_knowledge_tool",
        func=hsbc_knowledge_tool,
        description="useful for when you need to answer questions about hsbc related knowledge"
    ),
    Tool(
        name = "news_query_tool",
        func=news_query_tool,
        description="useful for when you need to answer questions about news"
    )
]

# Set up the base template
template = """Complete the objective as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

These were previous tasks you completed:

Begin!

Question: {input}
{agent_scratchpad}"""

# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]
    
    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]
    
class CustomOutputParser(AgentOutputParser):
    
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

output_parser = CustomOutputParser()

memory = ConversationBufferWindowMemory()

llm_chain = LLMChain(llm=llm_chat, prompt=prompt, output_parser=output_parser, memory=memory)
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, 
    output_parser=output_parser,
    stop=["\nObservation:"], 
    allowed_tools=tool_names
)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

agent_executor.run("How can I open an account with HSBC HK?")

agent_executor.run("What are the latest news?")





