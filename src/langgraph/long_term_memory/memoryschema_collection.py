import uuid
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore
from trustcall import create_extractor
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import merge_message_runs
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore


class Memory(BaseModel):
    content: str = Field(
        description="The main content of the memory. For example: User expressed interest in learning about French."
    )


class MemoryCollection(BaseModel):
    memories: list[Memory] = Field(description="A list of memories about the user.")


# Initialize the model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
# Bind schema to model
model_with_structure = model.with_structured_output(MemoryCollection)
# Invoke the model to produce structured output that matches the schema
memory_collection = model_with_structure.invoke(
    [HumanMessage("My name is Lance. I like to bike.")]
)
print(memory_collection.memories)
print(memory_collection.memories[0].model_dump())

# Initialize the in-memory store
in_memory_store = InMemoryStore()
# Namespace for the memory to save
user_id = "1"
namespace_for_memory = (user_id, "memories")
# Save a memory to namespace as key and value
key = str(uuid.uuid4())
value = memory_collection.memories[0].model_dump()
in_memory_store.put(namespace_for_memory, key, value)
key = str(uuid.uuid4())
value = memory_collection.memories[1].model_dump()
in_memory_store.put(namespace_for_memory, key, value)
# Search
for m in in_memory_store.search(namespace_for_memory):
    print(m.dict())

# UPDATING COLLECTION SCHEMA

# Create the extractor
trustcall_extractor = create_extractor(
    model,
    tools=[Memory],
    tool_choice="Memory",
    enable_inserts=True,
)

# Instruction
instruction = """Extract memories from the following conversation:"""
# Conversation
conversation = [
    HumanMessage(content="Hi, I'm Florentino."),
    AIMessage(content="Nice to meet you, Florentino."),
    HumanMessage(content="This morning I had a nice bike ride in San Francisco."),
]
# Invoke the extractor
result = trustcall_extractor.invoke(
    {"messages": [SystemMessage(content=instruction)] + conversation}
)
# Messages contain the tool calls
for m in result["messages"]:
    m.pretty_print()
# Responses contain the memories that adhere to the schema
for m in result["responses"]:
    print(m)
# Metadata contains the tool call
for m in result["response_metadata"]:
    print(m)
# Update the conversation
updated_conversation = [
    AIMessage(content="That's great, did you do after?"),
    HumanMessage(content="I went to Tartine and ate a croissant."),
    AIMessage(content="What else is on your mind?"),
    HumanMessage(content="I was thinking about my Japan, and going back this winter!"),
]

# Update the instruction
system_msg = """Update existing memories and create new ones based on the following conversation:"""
# We'll save existing memories, giving them an ID, key (tool name), and value
tool_name = "Memory"
existing_memories = (
    [
        (str(i), tool_name, memory.model_dump())
        for i, memory in enumerate(result["responses"])
    ]
    if result["responses"]
    else None
)
print(existing_memories)
# Invoke the extractor with our updated conversation and existing memories
result = trustcall_extractor.invoke(
    {"messages": updated_conversation, "existing": existing_memories}
)
# Messages from the model indicate two tool calls were made
for m in result["messages"]:
    m.pretty_print()
# Responses contain the memories that adhere to the schema
for m in result["responses"]:
    print(m)
# Metadata contains the tool call
for m in result["response_metadata"]:
    print(m)

# CHATBOT WITH COLLECTION SCHEMA UPDATING


# Memory schema
class Memory(BaseModel):
    content: str = Field(
        description="The main content of the memory. For example: User expressed interest in learning about French."
    )


# Create the Trustcall extractor
trustcall_extractor = create_extractor(
    model,
    tools=[Memory],
    tool_choice="Memory",
    # This allows the extractor to insert new memories
    enable_inserts=True,
)

# Chatbot instruction
MODEL_SYSTEM_MESSAGE = """You are a helpful chatbot. You are designed to be a companion to a user. 
You have a long term memory which keeps track of information you learn about the user over time.
Current Memory (may include updated memories from this conversation): 
{memory}"""

# Trustcall instruction
TRUSTCALL_INSTRUCTION = """Reflect on following interaction. 
Use the provided tools to retain any necessary memories about the user. 
Use parallel tool calling to handle updates and insertions simultaneously:"""


def call_model(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """Load memories from the store and use them to personalize the chatbot's response."""
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]
    # Retrieve memory from the store
    namespace = ("memories", user_id)
    memories = store.search(namespace)
    # Format the memories for the system prompt
    info = "\n".join(f"- {mem.value['content']}" for mem in memories)
    system_msg = MODEL_SYSTEM_MESSAGE.format(memory=info)
    # Respond using memory as well as the chat history
    response = model.invoke([SystemMessage(content=system_msg)] + state["messages"])
    return {"messages": response}


def write_memory(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """Reflect on the chat history and update the memory collection."""
    # Get the user ID from the config
    user_id = config["configurable"]["user_id"]
    # Define the namespace for the memories
    namespace = ("memories", user_id)
    # Retrieve the most recent memories for context
    existing_items = store.search(namespace)
    # Format the existing memories for the Trustcall extractor
    tool_name = "Memory"
    existing_memories = (
        [
            (existing_item.key, tool_name, existing_item.value)
            for existing_item in existing_items
        ]
        if existing_items
        else None
    )
    # Merge the chat history and the instruction
    updated_messages = list(
        merge_message_runs(
            messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION)] + state["messages"]
        )
    )
    # Invoke the extractor
    result = trustcall_extractor.invoke(
        {"messages": updated_messages, "existing": existing_memories}
    )
    # Save the memories from Trustcall to the store
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(
            namespace,
            rmeta.get("json_doc_id", str(uuid.uuid4())),
            r.model_dump(mode="json"),
        )


# Define the graph
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("write_memory", write_memory)
builder.add_edge(START, "call_model")
builder.add_edge("call_model", "write_memory")
builder.add_edge("write_memory", END)
# Store for long-term (across-thread) memory
across_thread_memory = InMemoryStore()
# Checkpointer for short-term (within-thread) memory
within_thread_memory = MemorySaver()
# Compile the graph with the checkpointer fir and store
graph = builder.compile(checkpointer=within_thread_memory, store=across_thread_memory)
# View
print(graph.get_graph(xray=1))
# We supply a thread ID for short-term (within-thread) memory
# We supply a user ID for long-term (across-thread) memory
config = {"configurable": {"thread_id": "1", "user_id": "1"}}
# User input
input_messages = [HumanMessage(content="Hi, my name is Florentino")]
# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
# User input
input_messages = [HumanMessage(content="I like to bike around Aarhus")]
# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
# Namespace for the memory to save
user_id = "1"
namespace = ("memories", user_id)
memories = across_thread_memory.search(namespace)
for m in memories:
    print(m.dict())
# User input
input_messages = [HumanMessage(content="I also enjoy going to bakeries")]
# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
# Continue the conversation in a new thread.
# We supply a thread ID for short-term (within-thread) memory
# We supply a user ID for long-term (across-thread) memory
config = {"configurable": {"thread_id": "2", "user_id": "1"}}
# User input
input_messages = [HumanMessage(content="What bakeries do you recommend for me?")]
# Run the graph
for chunk in graph.stream({"messages": input_messages}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()
