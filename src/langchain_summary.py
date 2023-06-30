from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate


def summarise_articles(
    chat_llm, text_splitter, article_headlines: list[str], article_texts: list[str]
) -> str:
    """Enriches news articles and texts with langchain stuff chain.
    Splits the text into chunks and summarises each chunk.
    :param chat_llm: ChatLLM object
    :param text_splitter: TextSplitter object
    :param article_headlines: List of article headlines
    :param article_texts: List of article texts
    :returns: A string containing the summarised articles.
    """

    # enrich the headlines with the article text
    enriched_headlines = [
        f"""headline: ```{headline}``` \
            article body: ```{article_text}```
            """
        for headline, article_text in zip(article_headlines, article_texts)
    ]

    # build prompt template
    summary_prompt = """
    Provided a news article headline and the news article body text in html format \
    enrich the headline with the body text and return the enriched headline which \
    should be no more than three sentences long. The enriched headline should \
    contain all the key information from the body text.

    {text}
    """
    summary_prompt_template = PromptTemplate(
        template=summary_prompt, input_variables=["text"]
    )

    # create summariser 'stuff' chain
    summary_chain = load_summarize_chain(
        chat_llm, chain_type="stuff", prompt=summary_prompt_template
    )

    # initialise final news text and progress bar
    final_news_text = ""

    # loop through and summarise docs with progress bar and summarised article texts
    for idx, text in enumerate(enriched_headlines):
        # check if text is a string; if not then skip
        if not isinstance(text, str):
            return_txt = f"Article: {idx+1}: No article text found"
            final_news_text += return_txt
            continue

        # split the text into chunks
        txt_split = text_splitter.split_text(text)
        txt_docs = [Document(page_content=txt) for txt in txt_split]

        # summarise the text
        try:
            summarised_doc = summary_chain.run(txt_docs)
        except Exception as e:
            return_txt = f"Article: {idx+1}: Error in summarising article: {e}"
            final_news_text += return_txt
            continue

        # add summarised doc to final news text
        summarised_doc = summarised_doc.replace("$", "\$")
        summarised_doc = f"Article {idx+1} {summarised_doc}\n\n"
        final_news_text += summarised_doc

    return final_news_text


def produce_meta_summary(chat_llm, text_splitter, text: str):
    """Provide a meta summary of enriched news headlines. Ranks in order of
    importance.
    :param chat_llm: ChatLLM object
    :param text_splitter: TextSplitter object
    :param text: A string containing the enriched news article headlines.
    :returns: A string containing the meta summary of the enriched news article headlines.
    """
    meta_summary_prompt = """
    Provided several enriched news article headlines, produce a \
    meta summary of the articles. Only use information from the text \
    given. And summarise the key information from the articles in \
    a numbered list ordered by their level of importance.

    text: ```{text}```
    """
    meta_prompt_template = PromptTemplate(
        template=meta_summary_prompt, input_variables=["text"]
    )
    summary_chain = load_summarize_chain(
        chat_llm, chain_type="stuff", prompt=meta_prompt_template
    )

    article_split = text_splitter.split_text(text)
    article_docs = [Document(page_content=txt) for txt in article_split]

    meta_summary = summary_chain.run(article_docs)
    meta_summary = meta_summary.replace("$", "\$")
    return meta_summary
