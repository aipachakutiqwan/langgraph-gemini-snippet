from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import RemoveMessage
from langchain_core.messages import trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI


# MESSAGE AS STATE
from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage

messages = [AIMessage(f"So you said you were researching ocean mammals?", name="Bot")]
messages.append(
    HumanMessage(
        f"Yes, I know about whales. But what others should I learn about?",
        name="Florentino",
    )
)

for m in messages:
    m.pretty_print()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

print(llm.invoke(messages))


# Node
def chat_model_node(state: MessagesState):
    return {"messages": llm.invoke(state["messages"])}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()
# View
print(graph.get_graph())

output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()

# REDUCER LONG RUNNING CONVERSATIONS


# Nodes
def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}


def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter")
builder.add_edge("filter", "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
print(graph.get_graph())

# Message list with a preamble
messages = [AIMessage("Hi.", name="Bot", id="1")]
messages.append(HumanMessage("Hi.", name="Florentino", id="2"))
messages.append(
    AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3")
)
messages.append(
    HumanMessage(
        "Yes, I know about whales. But what others should I learn about?",
        name="Florentino",
        id="4",
    )
)

# Invoke
output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()

# FILTERING MESSAGES


# Node
def chat_model_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"][-1:])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
print(graph.get_graph())

messages.append(output["messages"][-1])
messages.append(HumanMessage(f"Tell me more about Narwhals!", name="Florentino"))
for m in messages:
    m.pretty_print()

# Invoke, using message filtering
output = graph.invoke({"messages": messages})
for m in output["messages"]:
    m.pretty_print()


# TRIM MESSAGES: based upon a set number of tokens
# Node
def chat_model_node(state: MessagesState):
    messages = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",
        token_counter=ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        ),
        allow_partial=False,
    )
    return {"messages": [llm.invoke(messages)]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

# View
print(graph.get_graph())

messages.append(output["messages"][-1])
messages.append(HumanMessage(f"Tell me where Orcas live!", name="Florentino"))

# Example of trimming messages
trim_messages(
    messages,
    max_tokens=100,
    strategy="last",
    token_counter=ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    ),
    allow_partial=False,
)
# Invoke, using message trimming in the chat_model_node
messages_out_trim = graph.invoke({"messages": messages})

print("------------------------------------------------------")
for m in messages_out_trim["messages"]:
    m.pretty_print()
