# %%
import re
import subprocess
import json
import random
import datetime

from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

import local_init
import topics
import stories
# %%
prompt_template = """
I'm making a course of Italian language in the form of short stories
that develop the sense of language, improve vocabulary and demonstrate the
live language as it is used by natives. The target language level is B2.
The current story I'm working on is about "{theme}: {topic}".
Please write the text for the story. It should be engaging, sometimes funny and witty,
and have a twist. The story should be centered around a lively and dynamic dialogue,
with a few narrator lines that explain what is going on. Include vivid descriptions,
unexpected turns, and relatable characters. The dialogue should reflect natural
speech patterns and emotions, and the story should incorporate cultural elements
and idiomatic expressions to enrich the learning experience.

Key Elements to Include:

- Vivid Descriptions: Use sensory details to paint a clear picture of the setting and characters.
- Relatable Characters: Create characters with distinct personalities and relatable traits.
- Unexpected Turns: Introduce surprising elements or twists to keep the reader engaged.
- Cultural Elements: Incorporate aspects of Italian culture, traditions, or idiomatic expressions.
- Natural Dialogue: Ensure the dialogue flows naturally and reflects real-life conversations.
- Humor and Wit: Infuse the story with humor and cleverness to make it enjoyable.

Please write Italian story and its English translation.

Please limit the story to at most 20 lines in one language.

{format_output_instructions} 
"""
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=['theme', 'topic']
)

# %%
parser = PydanticOutputParser(pydantic_object=stories.Story)

# %%
topics_json = json.load(open('static/stories/topics.json'))
themes = topics.ThemeList.parse_obj(topics_json)
# %%
pairs = [(theme.theme, topic) for theme in themes.themes for topic in theme.topics]

# %%
theme, topic = random.choice(pairs)
# %%
gpt4o = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=local_init.openai_key)

chain = prompt | gpt4o | parser

story: stories.Story = chain.invoke({
    "format_output_instructions": parser.get_format_instructions(),
    "theme": theme,
    "topic": topic,
})

# %%
daily = stories.DailyStory(
    story=story,
    date=datetime.datetime.now().strftime("%Y-%m-%d"),
    theme=theme,
    topic=topic
)
# %%
with open(f'static/stories/daily-{daily.date}.json', 'w') as f:
    f.write(daily.json(indent=2))
# %%
