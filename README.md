# langgraph-gemini-snippet

Welcome to Python code snippet for LangGraph using Google Gemini (ChatGoogleGenerativeAI)!

## ⚡ Introduction

This repository contains a collection of code snippets designed to help you learn LangGraph using ChatGoogleGenerativeAI as the LLM backend. Its purpose is to provide concise examples that demonstrate core LangGraph concepts. Each script highlights a specific concept for easy understanding and experimentation.The snippets are inspired by the official LangGraph course, which is publicly available.

:heavy_exclamation_mark: **This snippet is not intended for direct use in production**. Do not use it as-is. Instead, use it as a reference: extract the core concept, refactor the code to suit your needs, write appropriate unit tests, and only then consider using it in a production environment.


## 📚 Content

:pushpin: Introduction

This module contains introductory code snippets for LangGraph, designed to demystify agents by explaining how they work in plain language. The examples demonstrate how to build simple agents using core abstractions such as states, nodes, and edges. You'll see how to construct graphs around chat models—specifically Gemini—using tools and messages. Finally, the module introduces a basic agent with memory.

:pushpin: State and Memory

This section provides code snippets demonstrating the importance of memory in agents, as users often expect agents to remember past interactions. It includes examples of implementing memory and adding persistence to the graph using both internal and external tools (SQLite). Techniques such as trimming, filtering, and summarization are used to manage long message histories effectively.

:pushpin: Human in the Loop

These code snippets demonstrate how to incorporate human approval before executing certain actions using breakpoints, as well as how to update graph states based on user input. LangGraph Studio is used to debug and visualize the agents behaviour.


:pushpin: Building Assistant

This module includes a Research Assistant agent designed to streamline tedious and repetitive tasks. The agent operates with an overall goal broken down into subtasks, leveraging parallelization and subgraphs to optimize execution.


:pushpin: Long-term Memory

Includes code snippets demonstrating long-term memory, showing how to store conversations using dictionary-based data structures.

:pushpin: Deployment

This section provides an example of how to build agent code and deploy it as a container. Once deployed, the agent can be easily accessed and interacted with using the LangGraph SDK.



## :rocket: Setup

### 🌱  Create an environment and install dependencies

Check out the Contributing guide to learn how to set up the environment, install dependencies, and get started contributing to this repository.

### 🌱 Setting up env variables
You can use `.env` file for set the following enviromental variables.
```
export LANGCHAIN_API_KEY=SET_YOUR_API_KEY_HERE
export LANGCHAIN_TRACING_V2=true
export LANGSMITH_PROJECT=langgraph-gemini-snippet
export TAVILY_API_KEY=SET_YOUR_API_KEY_HERE
export GOOGLE_API_KEY=SET_YOUR_API_KEY_HERE
```

### 🌱 Google Gemini API
* Sign up [here](https://aistudio.google.com/apikey) and set `GOOGLE_API_KEY` in your environment

### 🌱 LangSmith
* Sign up for LangSmith [here](https://smith.langchain.com/) and set `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2=true` in your environment 

### 🌱 Tavily
* Tavily Search API is a search engine optimized for LLMs and RAG. Sign up [here](https://tavily.com/) and set `TAVILY_API_KEY` in your environment.

### 🌱 LangGraph Studio
* LangGraph Studio is a dedicated IDE for agentic systems, offering powerful tools for visualization, interaction, and debugging. To activate LangGraph Studio, run the following command in your terminal within the specific directory of each module:
```
langgraph dev
```