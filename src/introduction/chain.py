from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from src.model import llm

messages = [
    AIMessage(content="So you said you were researching ocean mammals?", name="Model")
]
messages.append(HumanMessage(content="Yes, that's right.", name="Florentino"))
messages.append(
    AIMessage(content="Great, what would you like to learn about.", name="Model")
)
messages.append(
    HumanMessage(
        content="I want to learn about the best place to see Orcas in the US.",
        name="Florentino",
    )
)
for m in messages:
    m.pretty_print()

result = llm.invoke(messages)
print(f"type(result): {type(result)}")
print(f"result: {result}")
print(f"result.response_metadata: {result.response_metadata}")

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply])
tool_call = llm_with_tools.invoke(
    [HumanMessage(content="What is 2 multiplied by 3", name="Florentino")]
)
print("tool_call.tool_calls: ", tool_call.tool_calls)

class MessagesState(MessagesState):
    pass

# Example adding messages to the state
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model"),
    HumanMessage(
        content="I'm looking for information on marine biology.", name="Florentino"
    ),
]
# New message to add
new_message = AIMessage(
    content="Sure, I can help with that. What specifically are you interested in?",
    name="Model",
)
# Add the new message to the initial messages
add_messages(initial_messages, new_message)

# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()
# Print graph
print(f"graph.get_graph: {graph.get_graph()}")
# Invoke the graph
messages = graph.invoke({"messages": HumanMessage(content="Hello!")})
for m in messages["messages"]:
    m.pretty_print()
# Invoke the graph
messages = graph.invoke({"messages": HumanMessage(content="Multiply 2 and 3")})
for m in messages["messages"]:
    m.pretty_print()
