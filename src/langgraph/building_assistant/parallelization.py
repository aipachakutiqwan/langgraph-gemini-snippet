import asyncio
from typing import Any
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import InvalidUpdateError
import operator
from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults
from langgraph_sdk import get_client


# FAN OUT / FAN IN
class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    state: str


class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state": [self._value]}


# Add nodes
builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
# Flow
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", "c")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
print(graph.get_graph())
print(graph.invoke({"state": []}))

builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
# Flow
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
print(graph.get_graph())
try:
    graph.invoke({"state": []})
except InvalidUpdateError as e:
    print(f"An error occurred: {e}")


class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    state: Annotated[list, operator.add]


# Add nodes
builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
# Flow
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
print(graph.get_graph())
print(graph.invoke({"state": []}))

# Waiting for nodes to finish
builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("b2", ReturnNodeValue("I'm B2"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
# Flow
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b2")
builder.add_edge(["b2", "c"], "d")
builder.add_edge("d", END)
graph = builder.compile()
print(graph.get_graph())
print(graph.invoke({"state": []}))


# Setting the order of the state updates
def sorting_reducer(left, right):
    """Combines and sorts the values in a list"""
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]
    return sorted(left + right, reverse=False)


class State(TypedDict):
    # sorting_reducer will sort the values in state
    state: Annotated[list, sorting_reducer]


# Add nodes
builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("a", ReturnNodeValue("I'm A"))
builder.add_node("b", ReturnNodeValue("I'm B"))
builder.add_node("b2", ReturnNodeValue("I'm B2"))
builder.add_node("c", ReturnNodeValue("I'm C"))
builder.add_node("d", ReturnNodeValue("I'm D"))
# Flow
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b2")
builder.add_edge(["b2", "c"], "d")
builder.add_edge("d", END)
graph = builder.compile()
print(graph.get_graph())
print(graph.invoke({"state": []}))

# WORKING WITH LLMs
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


class State(TypedDict):
    question: str
    answer: str
    context: Annotated[list, operator.add]


def search_web(state):
    """Retrieve docs from web search"""
    # Search
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(state["question"])
    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}


def search_wikipedia(state):
    """Retrieve docs from wikipedia"""
    # Search
    search_docs = WikipediaLoader(query=state["question"], load_max_docs=2).load()
    # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}">\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}


def generate_answer(state):
    """Node to answer a question"""
    # Get state
    context = state["context"]
    question = state["question"]
    print(f"Context: {context}")
    print(f"Question: {question}")
    # Template
    answer_template = """Answer the question {question} using this context: {context}"""
    answer_instructions = answer_template.format(question=question, context=context)
    # Answer
    answer = llm.invoke(
        [SystemMessage(content=answer_instructions)]
        + [HumanMessage(content=f"Answer the question.")]
    )
    # Append it to state
    return {"answer": answer}


# Add nodes
builder = StateGraph(State)
# Initialize each node with node_secret
builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)
# Flow
builder.add_edge(START, "search_wikipedia")
builder.add_edge(START, "search_web")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("generate_answer", END)
graph = builder.compile()
print(graph.get_graph())
result = graph.invoke({"question": "How were Nvidia's Q2 2024 earnings"})
print(result["answer"].content)


# USING LANGGRAPH API
async def search():
    print(f"Running parallelization example with LangGraph API")
    client = get_client(url="http://127.0.0.1:2024")
    thread = await client.threads.create()
    input_question = {"question": "How were Nvidia Q2 2024 earnings?"}
    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="parallelization",
        input=input_question,
        stream_mode="values",
    ):
        # Check if answer has been added to state
        answer = event.data.get("answer", None)
        if answer:
            print(answer["content"])


asyncio.run(search())
