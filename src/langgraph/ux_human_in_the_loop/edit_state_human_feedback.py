import asyncio
from langgraph_sdk import get_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, SystemMessage


# EDITING STATE
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def divide(a: int, b: int) -> float:
    """Divide a by b.

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [add, multiply, divide]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(
    content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
)


# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Graph
builder = StateGraph(MessagesState)
# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
# Define edges: these determine the control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")
memory = MemorySaver()
graph = builder.compile(interrupt_before=["assistant"], checkpointer=memory)
# Show
print(graph.get_graph(xray=True))

# Input
initial_input = {"messages": "Multiply 2 and 3"}
# Thread
thread = {"configurable": {"thread_id": "1"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
state = graph.get_state(thread)
print(f"state: {state}")
# update the state with a new message
graph.update_state(
    thread,
    {"messages": [HumanMessage(content="No, actually multiply 3 and 3!")]},
)
new_state = graph.get_state(thread).values
for m in new_state["messages"]:
    m.pretty_print()
# Continue the graph from the updated state
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
# let continue to the result
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

# EDITING GRAPH STATE IN STUDIO


async def edit_state():
    # This is the URL of the local development server
    client = get_client(url="http://127.0.0.1:2024")
    initial_input = {"messages": "Multiply 2 and 3"}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
        thread["thread_id"],
        "agent",
        input=initial_input,
        stream_mode="values",
        interrupt_before=["assistant"],
    ):
        print(f"Receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)
    current_state = await client.threads.get_state(thread["thread_id"])
    print(f"Current state: {current_state}")
    last_message = current_state["values"]["messages"][-1]
    print(f"Last message: {last_message}")
    last_message["content"] = "No, actually multiply 3 and 3!"
    print(f"Last message edited: {last_message}")
    await client.threads.update_state(thread["thread_id"], {"messages": last_message})
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=None,
        stream_mode="values",
        interrupt_before=["assistant"],
    ):
        print(f"Stream 1 receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=None,
        stream_mode="values",
        interrupt_before=["assistant"],
    ):
        print(f"Stream 2 receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)


# asyncio.run(edit_state())

# AWAITING USER INPUT
# System message
sys_msg = SystemMessage(
    content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
)


# no-op node that should be interrupted on
def human_feedback(state: MessagesState):
    pass


# Assistant node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# Graph
builder = StateGraph(MessagesState)
# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_feedback", human_feedback)
# Define edges: these determine the control flow
builder.add_edge(START, "human_feedback")
builder.add_edge("human_feedback", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "human_feedback")
memory = MemorySaver()
graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)
print(graph.get_graph())
# Input
initial_input = {"messages": "Multiply 2 and 3"}
# Thread
thread = {"configurable": {"thread_id": "5"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
# Get user input
user_input = input("Tell me how you want to update the state: ")
# We now update the state as if we are the human_feedback node
graph.update_state(thread, {"messages": user_input}, as_node="human_feedback")
# Continue the graph execution
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
# Continue the graph execution
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
