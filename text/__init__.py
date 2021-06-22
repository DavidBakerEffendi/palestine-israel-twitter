import dash_html_components as html

introduction_summary = ["""
        The following introduction will cover both the socio-political scenario that is the 2021 Israel-Palestine crisis
        and the structure of how the resulting data from the public is processed. The introduction is then followed by
        the method and results of the processing the data using""", html.I("expert.ai"), """'s natural language 
        processing API. At the end we conclude our findings and explain potential future work on this kind of data.
        """]

introduction_conflict_1 = [
    """
    On May 10 2021 an outbreak of violence, looting, rocket attacks and protests commenced in 
    the ongoing Israeli-Palestinian conflict over the Gaza strip. The vector that began the main events of 
    May\'s crisis was on May 6 when a group of Palestinians began to protest in East Jerusalem. This was in 
    response to the trial happening in the Supreme Court of Israel on the eviction of six Palestinian families in 
    Sheikh Jarrah. This eviction is long legal battle against right-wing Jewish Israelis trying to acquire property in 
    the neighbourhood. Sheikh Jarrah is a primarily Palestinian neighbourhood but it is effectively annexed by Israel 
    and under military control. 
    """,
    """
    As anger grew around the potential eviction, Palestinian youth began throwing rocks at Israeli police force from
    Jerusalem’s Al-Aqsa Mosque. Al-Aqsa Mosque is considered Islam's third holiest site and is also known as Temple 
    Mount. Hundreds of police responded with firing rubber bullets and stun grenades at thousands of Palestinians which 
    resulted in 205 Palestinians and 17 officers being injured. Already at this point had the violence drawn 
    international protests and calls for peace from world leaders.
    """,
]

introduction_conflict_2 = [
    """
    The clashes coincided with Qadr Night (8 May) and Jerusalem Day (9-10 May) observed by Muslims and Jews 
    respectively. At this point more than 700 Palestinians were injured. By 10 May Hamas, a Palestinian Sunni-Islamic 
    fundamentalist, militant, and nationalist organization, gave Israel an ultimatum to withdraw security forces from 
    Temple Mount and Sheikh Jarrah by 6PM otherwise consequences will follow. The ultimatum was not met with a response 
    and Hamas proceeded to launch rockets at Israel of which most were intercepted by Israel's Iron Dome defense system.
    Those of which managed to pass through hit residences and a school. Israel responded with multiple airstrikes 
    against Gaza demolishing buildings including schools, hospitals, and refugee camps. On 13 May Hamas first proposed a 
    ceasefire which was rejected by Israeli prime minister Benjamin Netanyahu.
    """,
    """
    The period between 10 May and the initial cease-fire on 21 May left 256 Palestinians including 66 children dead, 
    whereas Israel was left with at least 13 deaths, two of which were children. Casualties and displaced civilians were
    majority Palestinian and in the thousands. By 21 May a ceasefire came into effect, but this was ultimately broken on
    16 June when Hamas launched incendiary balloons into Israel. The Israeli Air Force responded by carrying out 
    multiple airstrikes in the Gaza strip.
    """
]

introduction_problem = [
    """
    The crisis is one deeply rooted in political and religious debate in the ongoing Israeli-Palestinian conflict,
    marked as taking place since the mid-20th century. Opinions of the crisis from both sides are vocal on social media 
    followed with day-to-day mainstream media coverage. Both the mainstream media and public opinion are vulnerable to
    bias and misinformation. While bias requires more advanced context-specific techniques to analyze, we can already 
    mine sentiment and opinion.
    """,
    """
    In this project we would like to mine the sentiment, behavioural, and emotional traits from Tweets
    and articles by various media outlets. Both Twitter and media outlets produce masses of data that require 
    sophisticated processing techniques. We hope to identify: (i) Patterns which may or may not exist between the public
    and the media i.e. whether the media influences the masses or whether the media misrepresents public opinion on 
    divisive matters. (ii) Whether the media would step outside the bounds of objectivity towards an emotional response
    if pushed by mounting public pressure.
    """
]

method_summary = [
    """
    In this section we describe how we mine our data and the proceeding analysis. Our Twitter dataset is mined via the
    Twitter API 2.0 using the academic research product track, results cleaned using NLTK, and then further processed by 
    expert.ai's classification and sentiment analysis endpoints.
    """
]

data_mining = [
    """
    To obtain a large enough amount of data to analyze, Twitter and a set of mainstream media article URLs were mined 
    for natural language covering the event. In total, 130 267 tweets and 165 media articles were mined to create our 
    dataset. The time period was bound from 8 May, when protests ramped up at Temple Mount, until 21 May, when the 
    initial ceasefire order was taken into effect. All of the results retain temporal information as the results are 
    aggregated per day.
    """
]

twitter_mining_1 = [
    """
    A few handpicked hashtags are used to identify tweets covering the events of the crisis. Using the Twitter 2.0 API,
    the tweets are pulled with language information and creation date. Since most of expert.ai's natural language
    processing is bound to English, other languages are filtered out.
    """,
    """
    On the timelines of related tweets, the pro-Palestine hashtags are most diverse, but both sides are fairly equally
    represented. Neutral hashtags are also included to help balance the kinds of tweets that are being 
    pulled. Below are the hashtags used.
    """
]

twitter_mining_2 = [
    """
    Only English tweets are kept and all unicode is filtered out before sending the tweets for analysis.
    """,
]

media_mining = [
    html.P("""
    For this portion of the data mining, URLs are handpicked and then automatically scraped for content. The media 
    outlets picked are:
    """),
    html.Ul(
        [
            html.Li("EWN"),
            html.Li("BBC"),
            html.Li("The Associated Press"),
            html.Li("The Guardian"),
        ]
    ),
    html.P("""
        Articles are much larger than a single tweet so each article was rich in content so fewer were necessary
        to get a comprehensive view of the media's perspective. For most websites, scraping content with BeautifulSoup
        is sufficient but The Associated Press generates their pages with JavaScript so Selenium is required to render
        the content before scraping text.
        """),
]

language_processing = [
    """
    Expert.ai's sentiment, key phrases, emotional traits, and behavioral traits endpoints are used to analyze the
    language data. Due to the character limit per request, media article results are chunked and aggregated to represent
    the article analyzed.
    """,
    """
    The analysis is separated by Twitter results and media results. The key phrases and traits analysis returns each
    item with a score. For each day, the scores were aggregated and the mean is used to determine the score for each
    phrase or trait.
    """,
    """
    For each phrase or trait there may be a match in when both Twitter and the media used them in their text. These
    matches are scored with the context of their day by putting all the matches in a list, obtaining the absolute
    difference in their scores, and normalizing the scores in that list on an interval between 0-1. With this kind of 
    scoring, the lower number indicates a higher correlation so the results are then inverted to reflect higher 
    correlation with a higher value. This is then later used as a percentage to compare the quality of matches with a 
    higher percentage indicating a higher match.
    """,
]

results_summary = [
    """
    In this section we present the results of the experiments and data analysis. We find more interesting trends around
    how emotions and behavior correlate but also important matches across the board around large events.
    """
]

sentiment_paragraph = [
    """
    Below we show a graph of the sentiment extracted from both datasets aggregated per day. This includes error bars
    that show the standard deviation in sentiment per plot point.
    """,
    """
    The Twitter data has a large variance in the sentiment and so outliers were removed using the z-score but this
    unfortunately did not help too much. This may indicate a lot of noise in the Twitter data for unrelated Tweets or
    that Tweets are not very well-suited to sentiment analysis. The quality of the sentiment for media articles showed 
    much more consistency with sentiment gradually rising towards the beginning of the ceasefire but still remaining 
    much lower than the average sentiment over the Twitter data.
    """,
    """
    The Twitter sentiment does not appear to vary at all and remains consistent over the duration of the interval but 
    sentiment may not be the best indication of opinion from Twitter as it is for the media articles which are much
    less noisy. One key difference is in how the data is mined and key words used to detect relevant articles are much
    more effective. 
    """
]

phrases_trait_summary = [
    """
    In the following we take a closer look at the key phrases and traits extracted from each day's data. We also see
    how certain phrases or traits are matched between the public and the media. In the legend below we color-code and
    sort the items by the score of their impact.
    """
]

key_phrases_paragraph = [
    """
    When looking at the key phrases used between the two datasets, it is clear that the public and media are fairly
    different. When looking at the Twitter data there are clearly repeated phrases that score higher and make a larger 
    impact but in the media most phrases are scored consistently and there is less repetition. When looking at each
    dataset's list in isolation the results are not very interesting. This changes when we look at the matches and we
    can see a correlation in the important facts that we being carried across both platforms.
    """,
    """
    Certain phrases such as "compound", "police", or "rocket" only matching at a high rate days after an event 
    illustrate the delay in which news of an event impacts the public and the media at the same time. The matches also
    appear to show what are the most impactful events.
    """
]

e_traits_paragraph = [
    """
    Looking towards the emotional traits extracted from the text we immediately see the expected result of most 
    emotional traits scoring fairly mildly in the media articles as the media are meant to present stories factually and
    without bias. Twitter is often a place for the public to rant and debate so it is not a surprise to see high scores
    for key emotions.
    """,
    """
    Many of the matches here are on how low-scoring emotions matched strongly on either side but we do see shared
    opinions between the two datasets. Many of the strong matches occur a day or two after highly violent events and 
    only growing throughout the interval.
    """
]

b_traits_paragraph = [
    """
    The behavioral traits show the consistently highest rate of correlation over the interval. Both sides show strong
    scores for certain behaviours and often these are the same ones over each day.
    """,
    """
    At the beginning of the interval we see matches on negative and emotional behaviors and during the middle we see the 
    introduction of solidarity, compassion, and empathy. Towards the end we see apprehension, hope, and introversion 
    scoring much higher as the worst of the conflict comes to an end.
    """
]

sim_paragraph = [
    """
    The graph below shows the mean similarity score based on the matches for the key phrases and traits. Spikes in these
    appear to happen around significant events whereas key phrases hit local maxes around big events such as the start
    of Israel's airstrike campaign on 11 May.
    """,
    """
    The behavioral traits began to peak around the time Israel rejected Hamas' initial ceasefire proposal. These 
    remained at a high and consistent similarity until the end of the interval. The largest spike in emotional traits
    was when Israel targeted and destroyed a building which housed Associated Press journalists on 15 May and then 
    peaked once more at the beginning of the ceasefire.
    """,
    """
    This graph shows that there is a much higher similarity in emotional and behavioral traits between tweet and media
    articles which suggests that analyzing the sub-text of the two datasets are more useful in determining the impact
    of events and correlation between the public and the media.
    """
]

conclusion = [
    """
    The sentiment over the events of the 2021 Israel-Palestine crisis was unsurprising low due to the international
    condemnation of the violence and human rights violations that occurred. In our results we show that key phrases
    may show us what about each event made the largest impact internationally but not necessarily where the media
    and public share a strong link.
    """,
    """
    We show, from the similarity in the emotional and behavioral traits of our data, that patterns do in fact emerge
    in the wake of events that bring out passionate emotions and international attention. Over the course of the crisis
    the public was vocal from the beginning and showed strong emotions which were eventually followed by in media
    coverage. These two datasets show us that the media will step outside the bounds of objectivity in extreme
    humanitarian crisis and that despite any bias or misinformation that the feelings of condemnation are consistent.
    """
]

future_work = [
    """
    The bias in opinion in this event was clear, mostly from the public, and would certainly be a valuable 
    study to see if this is present in the media and/or when this changes. Using knowledge graphs one could perhaps 
    gather the kinds of facts the media will decide to communicate and which are withheld but seeing what is being
    covered by the public.
    """,
    """
    These trends may suggest applications in using neural networks, perhaps graph neural networks, to predict the level
    of impact these kinds of events generate over time given the live input and reaction we can mine key phrases and 
    traits from. 
    """
]