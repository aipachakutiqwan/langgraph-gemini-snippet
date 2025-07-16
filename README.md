# langgraph-gemini-snippet

Welcome to Python code snippet for LangGraph using Google Gemini (ChatGoogleGenerativeAI)!

## ⚡ Introduction

This repository contains a collection of code snippets designed to help you learn LangGraph using ChatGoogleGenerativeAI as the LLM backend. Its purpose is to provide concise examples that demonstrate core LangGraph concepts. Each script highlights a specific concept for easy understanding and experimentation.The snippets are inspired by the official LangGraph course, which is publicly available.

:heavy_exclamation_mark: This snippet is not intended for direct use in production. Do not use it as-is. Instead, use it as a reference: extract the core concept, refactor the code to suit your needs, write appropriate unit tests, and only then consider using it in a production environment.


## 📚 Content

- Introduction
- State and Memory
- Human in the Loop
- Building Assistant
- Long-term Memory
- Deployment


## :rocket: Setup

### 🌱  Create an environment and install dependencies

Follow the Contribuiting to learn how to create environment, install dependencies and of course contribuite to this repository!

### 🌱 Setting up env variables
You can use a `.env` file for set the enviromental variables. Use the following variables.
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

### 🌱 Tavily API
* Tavily Search API is a search engine optimized for LLMs and RAG, sign up [here](https://tavily.com/) and set `TAVILY_API_KEY` in your environment.

### 🌱 LangGraph Studio
* LangGraph Studio is a custom IDE for viewing and testing agents. Run the following command in your terminal in the specific directory of each module:
```
langgraph dev
```
## 🔭 Next improvements