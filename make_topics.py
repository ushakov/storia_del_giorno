# %%
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

import local_init
import topics
# %%
prompt_template = """
I'm making a course of Italian language in the form of short stories that develop the sense of language,
improve vocabulary and demonstrate the live language as it is used by natives.
Please suggest 30 themes and topics around which these stories will be created.
(Inside each topic there will be multiple stories). The target language level is C1.

{format_output_instructions} 
"""
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=[]
)

# %%
parser = PydanticOutputParser(pydantic_object=topics.ThemeList)

# %%
print(parser.get_format_instructions())

# %%
gpt4o = ChatOpenAI(temperature=0.0, model="gpt-4o",
                   openai_api_key=local_init.openai_key)

chain = prompt | gpt4o | parser

themes: topics.ThemeList = chain.invoke({"format_output_instructions": parser.get_format_instructions()})

# %%
with open('static/stories/topics.json', 'w') as f:
    f.write(themes.json(indent=2))
# %%
