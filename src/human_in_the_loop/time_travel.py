from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, SystemMessage

from src.model import llm


# REPLAY
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
graph = builder.compile(checkpointer=MemorySaver())
# Show
print(graph.get_graph(xray=True))
# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
# Thread
thread = {"configurable": {"thread_id": "1"}}
# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()
graph.get_state({"configurable": {"thread_id": "1"}})
all_states = [s for s in graph.get_state_history(thread)]
print(f"all_states: {all_states[-2]}")
to_replay = all_states[-2]
print(f"to_replay: {to_replay}")
print(f"to_replay.values: {to_replay.values}")
print(f"to_replay.next: {to_replay.next}")
print(f"to_replay.config: {to_replay.config}")
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# FORKING
to_fork = all_states[-2]
to_fork.values["messages"]
print(f"to_fork.config: {to_fork.config}")
fork_config = graph.update_state(
    to_fork.config,
    {
        "messages": [
            HumanMessage(
                content="Multiply 5 and 3", id=to_fork.values["messages"][0].id
            )
        ]
    },
)
print(f"fork_config: {fork_config}")
all_states = [state for state in graph.get_state_history(thread)]
print(all_states[0].values["messages"])
print(graph.get_state({"configurable": {"thread_id": "1"}}))
for event in graph.stream(None, fork_config, stream_mode="values"):
    event["messages"][-1].pretty_print()
print(graph.get_state({"configurable": {"thread_id": "1"}}))
