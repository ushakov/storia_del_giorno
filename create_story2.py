# %%
import json
import random
import datetime

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)


from langchain.output_parsers import PydanticOutputParser

import local_init
import topics
import stories
# %%
chat_template = [
    SystemMessage(content="You are an expert teacher of foreign languages but also a witty person with great sense of humor."),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}"),
]
prompt_template = ChatPromptTemplate.from_messages(chat_template)

# %%
parser = PydanticOutputParser(pydantic_object=stories.Story)

# %%
gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=1,
    openai_api_key=local_init.openai_key)

gpt4o_structured = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=local_init.openai_key)


memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
chain = LLMChain(llm=gpt4o, prompt=prompt_template, memory=memory)
chain_structured = LLMChain(llm=gpt4o_structured, prompt=prompt_template, memory=memory)

# %%
topics_json = json.load(open('static/stories/topics.json'))
themes = topics.ThemeList.parse_obj(topics_json)
# %%
pairs = [(theme.theme, topic)
         for theme in themes.themes for topic in theme.topics]

# %%
theme, topic = random.choice(pairs)
# %%
stage_1_prompt = """
I'm making a course of Italian language in the form of short stories
that develop the sense of language, improve vocabulary and demonstrate the
live language as it is used by natives. The target language level is B1.
The current story I'm working on is about "{theme}: {topic}".
The story should be engaging and funny, and have an unexpected twist.
The story should be centered around a lively and dynamic dialogue, not more than 10 turns,
with a few narrator lines that explain what is going on. Include
unexpected turns and relatable characters. The dialogue should reflect natural
speech patterns and emotions, and the story should incorporate cultural elements
and idiomatic expressions to enrich the learning experience.

Key Elements to Include:

- Relatable Characters: Create characters with distinct personalities and relatable traits.
- Unexpected Turns: Introduce surprising elements or twists to keep the reader engaged.
- Cultural Elements: Incorporate aspects of Italian culture, traditions, or idiomatic expressions.
- Natural Dialogue: Ensure the dialogue flows naturally and reflects real-life conversations.
- Humor and Wit: Infuse the story with humor and cleverness to make it enjoyable.

Please write a one-paragraph summary of the story. Include any unexpected twists or
key elements you plan to incorporate. Do not include the story itself, just a brief summary.
Please keep the tone lively and fun, with no moralizing or didactic elements, and don't include
a summarizing comment at the end. 
""".format(theme=theme, topic=topic)


stage_2_prompt = """Thanks! Now please write the story in Italian.

It should be a dialogue, with a few narrator lines and no other text. It should contain no more than 10 turns.
Do not write remarks or explanations, just the dialogue and the narrator lines.
Please keep the tone lively and fun, with no moralizing or didactic elements, and don't include
a summarizing comment at the end (i.e. don't write "E così, tra A e B, ...")
"""

stage_3_prompt = """Great! Now add the English translation.

{instructions}
""".format(instructions=parser.get_format_instructions())

# %%
def create_story():
    abstract = chain.invoke(stage_1_prompt)
    abstract = abstract['text']
    print(abstract)
    _ = chain.invoke(stage_2_prompt)
    res = chain_structured.invoke(stage_3_prompt)
    return parser.parse(res['text']), abstract

# %%
for _ in range(5):
    try:
        story, abstract = create_story()
        break
    except Exception as e:
        print(e)
        continue

# %%
daily = stories.DailyStory(
    story=story,
    abstract=abstract,
    date=datetime.datetime.now().strftime("%Y-%m-%d"),
    theme=theme,
    topic=topic
)
# %%
with open(f'static/stories/daily-{daily.date}.json', 'w') as f:
    f.write(daily.json(indent=2))

# %%
