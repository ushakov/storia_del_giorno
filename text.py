import json
import random
from dataclasses import dataclass, asdict

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

import topics
import stories


chat_template = [
    SystemMessage(content="You are an expert teacher of foreign languages but also a witty person with great sense of humor."),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}"),
]
prompt_template = ChatPromptTemplate.from_messages(chat_template)

parser = PydanticOutputParser(pydantic_object=stories.Story)

gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=1)

gpt4o_structured = ChatOpenAI(
    model="gpt-4o",
    temperature=0)

stage_1_prompt_template = """
    I'm making a course of {target_language} language in the form of short stories
    that develop the sense of language, improve vocabulary and demonstrate the
    live language as it is used by natives. The target language level is A2-B1
    so please keep the language simple and clear.
    The current story I'm working on is about "{theme}: {topic}".

    The story should be centered around a funny/comical situation that involves
    two or more characters. It will be focused on a dialogue between the characters
    with a few narrator lines that explain what is going on. Include
    unexpected turns and relatable characters. The dialogue should reflect natural
    speech patterns and emotions, and the story should incorporate cultural elements
    and idiomatic expressions to enrich the learning experience.

    Please imagine a comical situation and describe it in a one-paragraph summary.
    Do not write the story itself yet, just a brief description of the core comical situation.
    Please keep the tone lively and fun, with no moralizing or didactic elements, and don't include
    a summarizing comment at the end. 
    """

stage_2_prompt_template = """Thanks! Now please write the story in {target_language}.

    It should be a dialogue, with a few narrator lines and no other text. It should contain no more than 10 turns.
    Do not write remarks or explanations, just the dialogue and the narrator lines.
    Please keep the tone lively and fun, with no moralizing or didactic elements, and don't include
    a summarizing comment at the end (i.e. don't write "E così, tra A e B, ..."). Also, don't include remarks
    like "smiling" or "confused" in the dialogue, just the words the characters say.
    """

stage_3_prompt_template = """Great! Now add the English translation.

    {formatting_instructions}
    """


@dataclass
class SrcData:
    theme: str
    topic: str
    target_language: str
    formatting_instructions: str

    def fmt(self, text):
        return text.format(**asdict(self))

@dataclass
class StoryGenerator:
    target_language: str

    def try_creating_story(self, chain, chain_structured, src_data):
        abstract = chain.invoke(src_data.fmt(stage_1_prompt_template))
        abstract = abstract['text']
        print(abstract)
        _ = chain.invoke(src_data.fmt(stage_2_prompt_template))
        res = chain_structured.invoke(src_data.fmt(stage_3_prompt_template))
        return parser.parse(res['text']), abstract

    def generate_story(self):
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        chain = LLMChain(llm=gpt4o, prompt=prompt_template, memory=memory)
        chain_structured = LLMChain(llm=gpt4o_structured, prompt=prompt_template, memory=memory)

        topics_json = json.load(open('static/stories/topics.json'))
        themes = topics.ThemeList.parse_obj(topics_json)
        pairs = [(theme.theme, topic)
                for theme in themes.themes for topic in theme.topics]

        theme, topic = random.choice(pairs)

        src_data = SrcData(
            theme=theme,
            topic=topic,
            target_language=self.target_language,
            formatting_instructions=parser.get_format_instructions(),
        )

        for _ in range(5):
            try:
                story, abstract = self.try_creating_story(chain, chain_structured, src_data)
                break
            except Exception as e:
                print(e)
                continue

        return stories.DailyStory(
            language=self.target_language,
            story=story,
            abstract=abstract,
            theme=theme,
            topic=topic
        )

generator = StoryGenerator('Italian')