import asyncio
from langgraph_sdk import get_client


# EDITING GRAPH STATE IN STUDIO
# Activate the server by running: langgraph dev
async def edit_state():
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

asyncio.run(edit_state())
