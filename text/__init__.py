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
