import asyncio
from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client
from langchain_core.messages import convert_to_messages


# STREAMING WITH LANGGRAPH API
URL = "http://127.0.0.1:2024"

# Search all hosted graphs
async def call_assistants():
    # This is the URL of the local development server
    client = get_client(url=URL)
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
asyncio.run(call_assistants())


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
asyncio.run(call_assistants_streaming())


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
