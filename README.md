# HR RAG System

This project is a **Retrieval-Augmented Generation (RAG) chatbot** for answering HR-related questions using a hybrid .NET and Python architecture. It allows users to ask HR questions and receive intelligent, contextually relevant answers with source references from HR policy documents.

---

## Features

- **User registration** by username with automatic `Guid` assignment.
- **Question answering** using a Python-based RAG backend.
- **Sources returned** with every answer for transparency.
- **Response logging** including time, confidence, and source.
- **View query history** per user.
- Built with **.NET 8 (C# Web API)** and **Python RAG model**.
- Data saved in **PostgreSQL** via **Entity Framework Core**.

## Project Structure

HR_RAG/
│
├── HrRagApi/ # .NET Web API backend
│ ├── Controllers/ # API controllers
│ ├── Models/ # EF Core models
│ ├── Data/ # DbContext configuration
│ └── ...
│
├── rag_env/ # Python environment
│ ├── src/ # Python RAG model logic
│ ├── data/ # Text documents used for retrieval
│ └── requirements.txt # Python dependencies
│
└── README.md

# Usage Example
✅ POST /api/rag/ask

json
Copy
Edit
{
  "username": "mariam",
  "question": "What is the sick leave policy?"
}

# Tech Stack
- .NET 8 + Entity Framework Core
- Python 3.x (RAG model with text similarity + LLM)
- PostgreSQL
- Langchain / FAISS / HuggingFace (in Python backend)
- Swagger enabled for easy API testing

