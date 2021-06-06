from typing import List, Tuple, Dict

import numpy as np
from expertai.nlapi.cloud.client import ExpertAiClient
from expertai.nlapi.common.errors import ExpertAiRequestError
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
    import re
    text = text.encode("ascii", "ignore").decode()
    text = re.sub(r"\s+", " ", text, flags=re.UNICODE)
    return nltk.sent_tokenize(text)


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


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def lists_to_avgs(d: Dict[str, List[float]]) -> Dict[str, float]:
    out_dict = {}
    for k in d.keys():
        out_dict[k] = float(np.mean(d[k]))
    return out_dict


def analyze_text(text: str) -> Tuple[float, Dict[str, float], Dict[str, float], Dict[str, float]]:
    sent = []
    phrases = {}
    e_traits = {}
    b_traits = {}

    for chunk in chunks(clean_text(text), 50):
        payload = " ".join(chunk)
        # Sentiment
        try:
            sent.append(obtain_sentiment(payload))
        except ExpertAiRequestError as e:
            print("Error sending {}".format(payload))
            print(str(e))
            if "403" in str(e):
                exit(1)

        # Key phrases
        try:
            for x in obtain_key_phrases(payload):
                if x.value in phrases.keys():
                    phrases[x.value].append(x.score)
                else:
                    phrases[x.value] = [x.score]
        except ExpertAiRequestError as e:
            print("Error sending {}".format(payload))
            print(str(e))
            if "403" in str(e):
                exit(1)

        # Emotional traits
        try:
            for x in obtain_traits(payload):
                if x.label in e_traits.keys():
                    e_traits[x.label].append(x.score)
                else:
                    e_traits[x.label] = [x.score]
        except ExpertAiRequestError as e:
            print("Error sending {}".format(payload))
            print(str(e))
            if "403" in str(e):
                exit(1)

        # Behavioral traits
        try:
            for x in obtain_traits(payload, taxonomy="behavioral-traits"):
                if x.label in b_traits.keys():
                    b_traits[x.label].append(x.score)
                else:
                    b_traits[x.label] = [x.score]
        except ExpertAiRequestError:
            print("Error sending {}".format(payload))
            if "403" in str(e):
                exit(1)

    phrases, e_traits, b_traits = lists_to_avgs(phrases), lists_to_avgs(e_traits), lists_to_avgs(b_traits)
    return float(np.mean(sent)), phrases, e_traits, b_traits