import asyncio
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import START, END, StateGraph
from langgraph_sdk import get_client


class State(TypedDict):
    input: str


def step_1(state: State) -> State:
    print("---Step 1---")
    return state


def step_2(state: State) -> State:
    # Let's optionally raise a NodeInterrupt if the length of the input is longer than 5 characters
    if len(state["input"]) > 5:
        raise NodeInterrupt(
            f"Received input that is longer than 5 characters: {state['input']}"
        )
    print("---Step 2---")
    return state


def step_3(state: State) -> State:
    print("---Step 3---")
    return state


builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)
# Set up memory
memory = MemorySaver()
# Compile the graph with memory
graph = builder.compile(checkpointer=memory)
# View
print(graph.get_graph())

initial_input = {"input": "hello world"}
thread_config = {"configurable": {"thread_id": "1"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread_config, stream_mode="values"):
    print(event)
state = graph.get_state(thread_config)
print(state.next)
print(state.tasks)
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)
state = graph.get_state(thread_config)
print(state.next)
graph.update_state(
    thread_config,
    {"input": "hi"},
)
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)

# USE LANGGRAPH API

# This is the URL of the local development server


async def breakpoints():
    URL = "http://127.0.0.1:2024"
    client = get_client(url=URL)
    # Search all hosted graphs
    assistants = await client.assistants.search()
    thread = await client.threads.create()
    input_dict = {"input": "hello world"}
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="dynamic_breakpoints",
        input=input_dict,
        stream_mode="values",
    ):
        print(f"Receiving new event of type: {chunk.event}")
        print(chunk.data)
        print("\n\n")

    current_state = await client.threads.get_state(thread["thread_id"])
    current_state["next"]
    await client.threads.update_state(thread["thread_id"], {"input": "hi!"})
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="dynamic_breakpoints",
        input=None,
        stream_mode="values",
    ):
        print(f"Receiving new event of type: {chunk.event}")
        print(chunk.data)
        print("\n\n")
    current_state = await client.threads.get_state(thread["thread_id"])
    print(current_state)


asyncio.run(breakpoints())
