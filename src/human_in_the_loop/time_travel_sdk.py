import asyncio
from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage


# TIME TRAVEL WITH LANGGRAPH STUDIO
# REPLAY
async def replay():
    client = get_client(url="http://127.0.0.1:2024")
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=initial_input,
        stream_mode="updates",
    ):
        if chunk.data:
            assisant_node = chunk.data.get("assistant", {}).get("messages", [])
            tool_node = chunk.data.get("tools", {}).get("messages", [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])
    states = await client.threads.get_history(thread["thread_id"])
    to_replay = states[-2]
    print(f"to_replay: {to_replay}")
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=None,
        stream_mode="values",
        checkpoint_id=to_replay["checkpoint_id"],
    ):
        print("\n\n")
        print(f"Receiving new event of type: {chunk.event}")
        print(chunk.data)
    print("*" * 80)
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=None,
        stream_mode="updates",
        checkpoint_id=to_replay["checkpoint_id"],
    ):
        if chunk.data:
            assisant_node = chunk.data.get("assistant", {}).get("messages", [])
            tool_node = chunk.data.get("tools", {}).get("messages", [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])


asyncio.run(replay())


# FORKING
async def fork():
    client = get_client(url="http://127.0.0.1:2024")
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=initial_input,
        stream_mode="updates",
    ):
        if chunk.data:
            assisant_node = chunk.data.get("assistant", {}).get("messages", [])
            tool_node = chunk.data.get("tools", {}).get("messages", [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])
    states = await client.threads.get_history(thread["thread_id"])
    to_fork = states[-2]
    to_fork["values"]
    print(f"to_fork: {to_fork}")
    print(f"{to_fork['values']['messages'][0]['id']}")
    print(f"{to_fork['next']}")
    print(f"{to_fork['checkpoint_id']}")
    forked_input = {
        "messages": HumanMessage(
            content="Multiply 3 and 3", id=to_fork["values"]["messages"][0]["id"]
        )
    }
    forked_config = await client.threads.update_state(
        thread["thread_id"], forked_input, checkpoint_id=to_fork["checkpoint_id"]
    )
    print(f"forked_config: {forked_config}")
    states = await client.threads.get_history(thread["thread_id"])
    states[0]
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id="agent",
        input=None,
        stream_mode="updates",
        checkpoint_id=forked_config["checkpoint_id"],
    ):
        if chunk.data:
            assisant_node = chunk.data.get("assistant", {}).get("messages", [])
            tool_node = chunk.data.get("tools", {}).get("messages", [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])


asyncio.run(fork())
