from expertai.nlapi.cloud.client import ExpertAiClient
import config as conf


def publish_credentials():
    import os
    os.environ["EAI_USERNAME"] = conf.EXPERT_AI_USER
    os.environ["EAI_PASSWORD"] = conf.EXPERT_AI_PASS


def obtain_keyphrases(text:str, language='en'):
    client = ExpertAiClient()
    output = client.specific_resource_analysis(body={"document": {"text": text}},
                                               params={'language': language, 'resource': 'relevants'})
    # Output overall sentiment
    print("Main lemmas:")

    for lemma in output.main_lemmas:
        print(lemma.value)
    return output.main_lemmas


def obtain_sentiment(text: str, language='en'):
    client = ExpertAiClient()
    output = client.specific_resource_analysis(
        body={"document": {"text": text}},
        params={
            'language': language,
            'resource': 'sentiment'
        }
    )

    # Output overall sentiment
    print("Output overall sentiment:")
    print(output.sentiment.overall)
    return output.sentiment
