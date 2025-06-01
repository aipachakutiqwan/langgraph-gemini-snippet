import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph_sdk import get_client
from langchain_core.messages import convert_to_messages


# LLM
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


# State
class State(MessagesState):
    summary: str


# Define the logic to call the model
def call_model(state: State, config: RunnableConfig):
    # Get summary if it exists
    summary = state.get("summary", "")
    # If there is summary, then we add it
    if summary:
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"
        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    response = model.invoke(messages, config)
    return {"messages": response}


def summarize_conversation(state: State):
    # First, we get any existing summary
    summary = state.get("summary", "")
    # Create our summarization prompt
    if summary:
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"
    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


# Determine whether to end or summarize the conversation
def should_continue(state: State):
    """Return the next node to execute."""
    messages = state["messages"]
    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    # Otherwise we can just end
    return END


# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)
# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)
# Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
print(graph.get_graph())

# STREAMING FULL STATE
# Create a thread
config = {"configurable": {"thread_id": "1"}}
# Start conversation
for chunk in graph.stream(
    {"messages": [HumanMessage(content="hi! I'm Florentino")]},
    config,
    stream_mode="updates",
):
    print(chunk)
# Start conversation
for chunk in graph.stream(
    {"messages": [HumanMessage(content="hi! I'm Florentino")]},
    config,
    stream_mode="updates",
):
    chunk["conversation"]["messages"].pretty_print()

# Start conversation, again
config = {"configurable": {"thread_id": "2"}}
# Start conversation
input_message = HumanMessage(content="hi! I'm Conny")
for event in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    for m in event["messages"]:
        m.pretty_print()
    print("***" * 30)


# STREAMING TOKENS
async def streaming_tokens():
    config = {"configurable": {"thread_id": "3"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    async for event in graph.astream_events(
        {"messages": [input_message]}, config, version="v2"
    ):
        print(
            f"Node: {event['metadata'].get('langgraph_node','')}. Type: {event['event']}. Name: {event['name']}"
        )


# asyncio.run(streaming_tokens())


async def streaming_tokens_conversation():
    node_to_stream = "conversation"
    config = {"configurable": {"thread_id": "4"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    async for event in graph.astream_events(
        {"messages": [input_message]}, config, version="v2"
    ):
        # Get chat model tokens from a particular node
        if (
            event["event"] == "on_chat_model_stream"
            and event["metadata"].get("langgraph_node", "") == node_to_stream
        ):
            print(event["data"])

    config = {"configurable": {"thread_id": "5"}}
    input_message = HumanMessage(content="Tell me about the 49ers NFL team")
    async for event in graph.astream_events(
        {"messages": [input_message]}, config, version="v2"
    ):
        # Get chat model tokens from a particular node
        if (
            event["event"] == "on_chat_model_stream"
            and event["metadata"].get("langgraph_node", "") == node_to_stream
        ):
            data = event["data"]
            print(data["chunk"].content, end="|")


# asyncio.run(streaming_tokens_conversation())

# STREAMING WITH LANGGRAPH API
URL = "http://127.0.0.1:2024"


# Search all hosted graphs
async def call_assistants():
    # This is the URL of the local development server
    client = get_client(url=URL)
    assistants = await client.assistants.search()
    # Create a new thread
    thread = await client.threads.create()
    # Input message
    input_message = HumanMessage(content="Multiply 2 and 3")
    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input={"messages": [input_message]},
        stream_mode="values",
    ):
        print("event:", event)


# asyncio.run(call_assistants())


async def call_assistants_streaming():
    client = get_client(url=URL)
    thread = await client.threads.create()
    input_message = HumanMessage(content="Multiply 2 and 3")
    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input={"messages": [input_message]},
        stream_mode="values",
    ):
        messages = event.data.get("messages", None)
        if messages:
            print(convert_to_messages(messages)[-1])
        print("=" * 25)


# asyncio.run(call_assistants_streaming())


async def call_assistants_streaming_messages():
    client = get_client(url=URL)
    thread = await client.threads.create()
    input_message = HumanMessage(content="Multiply 2 and 3")
    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input={"messages": [input_message]},
        stream_mode="messages",
    ):
        print(event.event)


asyncio.run(call_assistants_streaming_messages())


async def format_calls():

    client = get_client(url=URL)
    thread = await client.threads.create()
    input_message = HumanMessage(content="Multiply 2 and 3")

    def format_tool_calls(tool_calls):
        """
        Format a list of tool calls into a readable string.
        Args:
            tool_calls (list): A list of dictionaries, each representing a tool call.
                Each dictionary should have 'id', 'name', and 'args' keys.
        Returns:
            str: A formatted string of tool calls, or "No tool calls" if the list is empty.
        """
        if tool_calls:
            formatted_calls = []
            for call in tool_calls:
                formatted_calls.append(
                    f"Tool Call ID: {call['id']}, Function: {call['name']}, Arguments: {call['args']}"
                )
            return "\n".join(formatted_calls)
        return "No tool calls"

    async for event in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input={"messages": [input_message]},
        stream_mode="messages",
    ):
        # Handle metadata events
        if event.event == "metadata":
            print(f"Metadata: Run ID - {event.data['run_id']}")
            print("-" * 50)
        # Handle partial message events
        elif event.event == "messages/partial":
            for data_item in event.data:
                # Process user messages
                if "role" in data_item and data_item["role"] == "user":
                    print(f"Human: {data_item['content']}")
                else:
                    # Extract relevant data from the event
                    tool_calls = data_item.get("tool_calls", [])
                    invalid_tool_calls = data_item.get("invalid_tool_calls", [])
                    content = data_item.get("content", "")
                    response_metadata = data_item.get("response_metadata", {})
                    if content:
                        print(f"AI: {content}")
                    if tool_calls:
                        print("Tool Calls:")
                        print(format_tool_calls(tool_calls))
                    if invalid_tool_calls:
                        print("Invalid Tool Calls:")
                        print(format_tool_calls(invalid_tool_calls))
                    if response_metadata:
                        finish_reason = response_metadata.get("finish_reason", "N/A")
                        print(f"Response Metadata: Finish Reason - {finish_reason}")
            print("-" * 50)


asyncio.run(format_calls())
