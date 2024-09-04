from pathlib import Path

import streamlit as st
import wikipedia
from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.agent import ReActAgent
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.schema import TextNode
from llama_index.core.tools import RetrieverTool, ToolMetadata, FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.readers.web import SimpleWebPageReader
from pydantic import BaseModel

wikipedia.set_lang("en")

system_prompt = "You are amazing trip planner."

llm = OpenAI(model="gpt-4o", temperature=0, system_prompt=system_prompt, timeout=120)

cities = {
    "Talinn": {
        "wiki_pages": [
            "Tallinn",
            "Estonia"
        ],
        "web_pages": [
            "https://whichmuseum.com/place/tallinn-2502/best-museums",
            "https://visiting.europarl.europa.eu/en/visitor-offer/other-locations/europa-experience/tallinn",
            "https://www.visittallinn.ee/eng/visitor/see-do/things-to-do/sports-adventure"
        ]
    },
}

group_types = [
            "Family with Kids",
            "Group of nerdy Python Developers",
            "Bachelor party"
        ]


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


class ItineraryStop(BaseModel):
    """
    Itinerary stop on a trip to given city.
    time_arrival and time_end MUST be in 24-hour format.
    name and description should contain emojis.
    name is specific attraction from itinerary
    description describes activity which group can do there
    """

    time_arrival: str
    time_end: str
    name: str
    description: str


class TravelItinerary(BaseModel):
    """Itinerary when visiting a given city consisting out of specific stops"""

    stops: list[ItineraryStop]


def gen_attractions(text: str) -> list[Attraction]:
    prompt_template_str = "Extract separate attractions a person can enjoy when visiting the city, including pubs, restaurants, parks, and more from a provided web page content {web_content}"

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=AttractionsInCity,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=True,
    )

    output = program(web_content=text)
    return output.attractions


def get_attractions(city: str):
    all_attractions = []

    wiki_pages = cities[city]["wiki_pages"]
    web_pages = cities[city]["web_pages"]

    for wiki_page in wiki_pages:
        print(f"Processing Wiki {wiki_page}")
        wiki_page_content = wikipedia.page(wiki_page).content
        all_attractions += gen_attractions(wiki_page_content)

    for web_page in web_pages:
        print(f"Processing Web {web_page}")
        web_page_content = SimpleWebPageReader(html_to_text=True).load_data(
            [web_page]
        )[0].text
        all_attractions += gen_attractions(web_page_content)

    return all_attractions


def generate_itinerary(city: str, group_type, start_time, end_time):
    print(city, group_type, start_time, end_time)

    index_dir_name = Path(f"./index_{city.lower()}/")
    if index_dir_name.exists():
        storage_context = StorageContext.from_defaults(persist_dir=index_dir_name)

        places_index = load_index_from_storage(storage_context)
    else:
        all_attractions = get_attractions(city)

        places_nodes = [TextNode(text=f"{p.name} - {p.description}") for p in all_attractions]
        places_index = VectorStoreIndex(places_nodes)

        places_index.storage_context.persist(persist_dir=index_dir_name)

    def check_opening_hours_tomorrow(place_name: str) -> bool:
        """
        Checks opening hours of place_name.
        Returns True if Place is open tomorrow.
        """
        return True

    def load_wikipedia_details(place_name: str) -> bool:
        """
        Loads information from Wikipedia
        """
        return wikipedia.page(place_name).content

    query_engine_tools = [
        RetrieverTool(
            places_index.as_retriever(similarity_top_k=3),
            metadata=ToolMetadata(
                name="city_places_list",
                description=(
                    "Searches interesting places in city based on place's description."
                    "Use detailed description what places are you looking for with examples."
                    "Describe if you are looking for restaurants, museums etc."
                ),
            ),
        ),
    ]

    # query_engine_tools += [FunctionTool.from_defaults(fn=load_wikipedia_details)]
    query_engine_tools += [FunctionTool.from_defaults(fn=check_opening_hours_tomorrow)]

    agent_prompt = f"""
Generate complete travel itinerary, starting at {start_time} and ending at {end_time} to a single day trip to {city}.
Trip is prepared for {group_type}.
Divide day into multiple parts and use tools for each of them separately.
Think about attractions and places to eat.
Mention concrete attractions you find using tools.
Ensure activities start at {start_time}.
Ensure activities are planned until {end_time}.
Ensure place is open tomorrow.
Look to wikipedia for more ideas if needed.
    """

    agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True, max_iterations=100)
    agent_response = agent.chat(agent_prompt).response
    print(agent_response)

    prompt_template_str = "Parse travel itinerary from provided text: {agent_response}"

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=TravelItinerary,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=True,
    )

    output = program(agent_response=agent_response)
    return output.stops


def main():
    st.title("City Trip Planner")

    city = st.selectbox(
        "Choose the city for your trip:",
        cities.keys(),
        index=0
    )

    group_type = st.radio(
        "Who is traveling?",
        group_types
    )

    start_time = st.selectbox(
        "Select the start time of your visit:",
        [f"{i}:00" for i in range(24)],  # 0:00 to 23:00
        index=8
    )

    end_time = st.selectbox(
        "Select the end time of your visit:",
        [f"{i}:00" for i in range(24)],
        index=17
    )
    if st.button('Generate Trip Itinerary'):
        itinerary = generate_itinerary(city, group_type, start_time, end_time)

        st.subheader(f'Travel Itinerary for *{group_type}* to *{city}* ', divider='rainbow')
        for item in itinerary:
            st.text_area(
                f"{item.time_arrival} - {item.time_end}: **{item.name}**",
                item.description
            )


if __name__ == "__main__":
    main()
