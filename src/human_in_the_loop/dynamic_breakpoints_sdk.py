import asyncio
from langgraph_sdk import get_client


# DYNAMIC BREAKPOINTS WITH LANGGRAPH SDK
# Activate the server by running: langgraph dev
async def breakpoints():
    URL = "http://127.0.0.1:2024"
    client = get_client(url=URL)
    # Search all hosted graphs
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
