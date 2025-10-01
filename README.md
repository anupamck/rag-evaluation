# RAG Evaluation

A rag model is built using the RAG tutorial from Langchain: https://python.langchain.com/docs/tutorials/rag/. Here, I have connected the [basecamp handbook ](https://basecamp.com/handbook) as the custom datasource, and used [Ragas](https://github.com/explodinggradients/ragas/tree/main/docs) for evaluating the RAG model's responses. 

This repo is linked to this [research task](https://github.com/BeyondQuality/beyondquality/blob/main/research/rag-evaluation.md) from the BeyondQuality community. 

## Setup
1. Get some credit and an API token from https://platform.openai.com/ (€5 should be more than enough)
2. Get an account at LangSmith: https://smith.langchain.com/ and create a project
3. Copy `.env_example` and rename it as `.env`(Should be gitignored) 
4. Add your API keys and project name from LangSmith to your `.env` file
   
## Quickstart (via Docker)
Prerequisite - You need to have installed Docker desktop on your machine. 
1. Build and start Jupyter Lab:
   ```bash
   docker compose up --build
   ```
2. Open your browser at `http://localhost:8888` (no token/password required).

Your current folder is mounted into the container at `/workspace`, so changes you make to notebooks and files are saved on your host.

To stop the server, press Ctrl+C in the terminal or run:
```bash
docker compose down
```

## Start without Docker
## Prerequisites 
- Python 3.10 or newer

1. Install all dependencies in requirements.txt, preferably in a python virtual environment
2. Open jupyter lab via `jupyter lab`
3. Execute the code in any of the Jupyter books (start with minimalRag, to follow along with [this LangChain tutorial](https://python.langchain.com/docs/tutorials/rag/#setup) )