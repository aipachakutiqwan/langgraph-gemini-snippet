import asyncio
from langgraph_sdk import get_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# BREAKPOINTS FOR HUMAN APPROVAL
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
graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)
# Show
print(graph.get_graph(xray=True))

# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
# Thread
thread = {"configurable": {"thread_id": "1"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

state = graph.get_state(thread)
print(f"state.next: {state.next}")
# Continue after interuption
for event in graph.stream(None, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
# Thread
thread = {"configurable": {"thread_id": "2"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
# Get user feedback
user_approval = input("Do you want to call the tool? (yes/no): ")
# Check approval
if user_approval.lower() == "yes":
    # If approved, continue the graph execution
    for event in graph.stream(None, thread, stream_mode="values"):
        event["messages"][-1].pretty_print()
else:
    print("Operation cancelled by user.")

# BREAKPOINTS WITH LANGGRAPH
# This is the URL of the local development server


async def breakpoint_example():
    client = get_client(url="http://127.0.0.1:2024")
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=initial_input,
        stream_mode="values",
        interrupt_before=["tools"],
    ):
        print(f"Receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)
    # Continue the run after the interruption
    async for chunk in client.runs.stream(
        thread["thread_id"],
        "agent",
        input=None,
        stream_mode="values",
        interrupt_before=["tools"],
    ):

        print(f"Receiving new event of type: {chunk.event}")
        messages = chunk.data.get("messages", [])
        if messages:
            print(messages[-1])
        print("-" * 50)


asyncio.run(breakpoint_example())
