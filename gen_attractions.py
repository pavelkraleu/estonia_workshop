import json
import sys

from llama_index.core.program import LLMTextCompletionProgram
from llama_index.readers.web import SimpleWebPageReader
from pydantic import BaseModel
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o", temperature=0, timeout=120)


class Attraction(BaseModel):
    """
    Attractions person can visit on a trip to given city.
    Name must be exact name of a place person can visit. For example Mendelovo muzeum, Cukrárna BezCukru
    Description should be a long text
    """
    name: str
    description: str


class AttractionsInCity(BaseModel):
    """List of attractions person can visit on a trip to given city"""
    attractions: list[Attraction]


def gen_attractions(text: str) -> AttractionsInCity:
    prompt_template_str = "Extract separate attractions a person can enjoy when visiting the city, including pubs, restaurants, parks, and more from a provided web page content {web_content}"

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=AttractionsInCity,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=True,
    )

    output = program(web_content=text)
    return output


web_page = sys.argv[1]

print(f"Processing page {web_page}")

web_page_content = SimpleWebPageReader(html_to_text=True).load_data(
    [web_page]
)[0].text

print(web_page_content)

attractions = gen_attractions(web_page_content)

attractions_dict = attractions.model_dump()

print(json.dumps(attractions_dict, indent=2))
