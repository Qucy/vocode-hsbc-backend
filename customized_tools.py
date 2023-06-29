
""" This is a file for custom tools that you can use in the LLM agent
"""
from langchain.tools import tool


@tool("Refinitiv freetext news search tool")
def refinitiv_freetext_news_summary_tool(input: str, num_weeks_ago: int) -> str:
    """
    Queries the Refinitiv News API for news articles related to the free text input
    which have happened in the last num_weeks_ago.
    Then summarises the news articles and returns the summaryy or enriched headlines.

    Refinitiv is better for English than Chinese news articles.
    """
    return


@tool("hsbc knowledge search tool")
def hsbc_knowledge_tool(input: str) -> str:
    """useful for when you need to answer questions about hsbc related knowledge"""
    # TODO need to be replace by vector search later
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


@tool("reject tool", return_direct=True)
def reject_tool(input: str) -> str:
    # LLM agent sometimes will not reject question not related to HSBC, hence adding this tools to stop the thought/action process
    """ useful for when you need to answer questions not related to HSBC """
    return """
    I'm sorry, but as a customer service chatbot for HSBC Hongkong, I am only able to assist with questions related to HSBC Hongkong products and services. 
    Is there anything else related to HSBC Hongkong that I can help you with?
    """
