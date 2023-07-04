""" This is a file for custom tools that you can use in the LLM agent
"""
import os

from dotenv import load_dotenv
from langchain.llms import AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import tool

from src.langchain_summary import produce_meta_summary, summarise_articles
from src.refinitiv_query import (
    create_rkd_base_header,
    parse_freetext_headlines,
    parse_news_stories_texts,
    retrieve_freetext_headlines,
    retrieve_news_stories,
)

# load environment variables
load_dotenv()

# set global variables
RKD_USERNAME = os.getenv("REFINITIV_USERNAME")
RKD_PASSWORD = os.getenv("REFINITIV_PASSWORD")
RKD_APP_ID = os.getenv("REFINITIV_APP_ID")

# Create an instance of Azure OpenAI; find completions is faster than chat
CHAT_LLM = AzureOpenAI(
    deployment_name="text-davinci-003",
    model_name="text-davinci-003",
    temperature=0,
    best_of=1,
)
TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=7_000, chunk_overlap=400)


@tool("Refinitiv freetext news search summary tool", return_direct=True)
def refinitiv_freetext_news_summary_tool(input: str) -> str:
    """
    Queries the Refinitiv News API for news articles related to the free text input
    which have happened in the last num_weeks_ago.
    Then summarises the news articles and returns the summary of enriched headlines.
    """
    base_header = create_rkd_base_header(RKD_USERNAME, RKD_PASSWORD, RKD_APP_ID)

    # freetext headline search; set last_n_weeks as 2; queries both headline and body
    # for english text (Refinitiv is better for English than Chinese queries).
    freetext_results = retrieve_freetext_headlines(base_header, input, 2, "both", "EN")
    freetext_news_articles = parse_freetext_headlines(freetext_results)

    # load full news stories related to those headlines
    news_stories = retrieve_news_stories(
        base_header, [article.id for article in freetext_news_articles]
    )
    news_stories_texts = parse_news_stories_texts(news_stories)

    # summarise the news stories
    article_summaries = summarise_articles(
        chat_llm=CHAT_LLM,
        text_splitter=TEXT_SPLITTER,
        article_headlines=[a.headline for a in freetext_news_articles],
        article_texts=news_stories_texts,
    )

    # produce meta summary
    meta_summary = produce_meta_summary(CHAT_LLM, TEXT_SPLITTER, article_summaries)
    return meta_summary


@tool("document question answering")
def document_question_answering(input: str) -> str:
    """
    For a given question, find the answer from a given document, load that document
    into a FAISS index and retrieve aspects relevant to the query. Then use
    using the langchain question answering chain to formulate answer.

    TODO: find a way to load the document; this is a work in progress. Maybe
    we can load documents directly based on input from a vector and QA dierctly.
    """

    # TODO: How to load files..
    # TODO: Do we actually want to implement this?

    return "TODO"


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
    """useful for when you need to answer questions not related to HSBC"""
    return """
    I'm sorry, but as a customer service chatbot for HSBC Hongkong, I am only able to assist with questions related to HSBC Hongkong products and services. 
    Is there anything else related to HSBC Hongkong that I can help you with?
    """
