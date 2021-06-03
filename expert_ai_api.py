from typing import List

from expertai.nlapi.cloud.client import ExpertAiClient
from expertai.nlapi.common.model import Category, MainLemma

import config as conf

client = None


def check_dependencies():
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')


def publish_credentials():
    import os
    global client
    os.environ["EAI_USERNAME"] = conf.EXPERT_AI_USER
    os.environ["EAI_PASSWORD"] = conf.EXPERT_AI_PASS
    client = ExpertAiClient()


def clean_text(text: str) -> List[str]:
    import nltk
    return [x.strip() for x in nltk.sent_tokenize(text)]


def obtain_key_phrases(text: str, language='en') -> List[MainLemma]:
    """
    Obtains the main key phrases from the given text.

    Example:

    for lemma in obtain_key_phrases(...,...):
        print(lemma.value)
    """
    global client
    if client is None:
        publish_credentials()
        client = ExpertAiClient()
    output = client.specific_resource_analysis(body={"document": {"text": text}},
                                               params={'language': language, 'resource': 'relevants'})
    return output.main_lemmas


def obtain_sentiment(text: str, language='en') -> float:
    """
    Obtain the sentiment for given text.
    """
    global client
    if client is None:
        publish_credentials()
        client = ExpertAiClient()
    output = client.specific_resource_analysis(
        body={"document": {"text": text}},
        params={
            'language': language,
            'resource': 'sentiment'
        }
    )

    return output.sentiment.overall


def obtain_traits(text: str, taxonomy='emotional-traits', language='en') -> List[Category]:
    """
    Obtains emotion or behavioural traits from given text. Taxonomy can be "emotional-traits" or "behavioral-traits".

    Example using the output:

    for category in obtain_traits(...,...,...):
        print(category.id_, category.hierarchy, sep="\t")
    """
    global client
    if client is None:
        publish_credentials()
        client = ExpertAiClient()
    output = client.classification(body={"document": {"text": text}},
                                   params={'taxonomy': taxonomy, 'language': language})
    return output.categories
