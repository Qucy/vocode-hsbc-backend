from src.langchain_summary import summarise_articles, produce_meta_summary
from langchain.llms import AzureOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=7_000, chunk_overlap=400)
CHAT_LLM = AzureOpenAI(
    deployment_name="text-davinci-003",
    model_name="text-davinci-003",
    temperature=0,
    best_of=1,
)


def test_summarise_articles():
    """Test summarising articles."""

    # list of sample article headlines and texts
    headlines = [
        "Breaking News: Fire at City Hall",
        "Local Sports Team Wins Championship",
        "New Park Opens Downtown",
    ]
    texts = [
        "A fire broke out at City Hall earlier today, causing significant damage to the building. Firefighters were able to contain the blaze and no injuries were reported.",
        "The local sports team won the championship game last night in a thrilling match against their rivals. Fans celebrated in the streets after the victory.",
        "A new park opened downtown today, featuring a playground, picnic areas, and walking trails. The park is expected to be a popular destination for families and outdoor enthusiasts.",
    ]
    article_summaries = summarise_articles(
        CHAT_LLM,
        text_splitter,
        headlines,
        texts,
    )
    assert isinstance(article_summaries, str)


def test_meta_summary():
    """Test meta summary."""
    article_summaries = """
    Article 1 
    Enriched headline: Breaking News: Fire at City Hall Causes Significant Damage, Contained by Firefighters with No Injuries Reported.

    Article 2 
    Enriched headline: ```Local Sports Team Wins Championship in Thrilling Match Against Rivals, Sparking Celebrations in the Streets```

    Article 3 
    Enriched headline: ```New Park Opens Downtown, Featuring Playground, Picnic Areas, and Walking Trails for Families and Outdoor Enthusiasts```
    """
    meta_summary = produce_meta_summary(CHAT_LLM, text_splitter, article_summaries)
    assert isinstance(meta_summary, str)
