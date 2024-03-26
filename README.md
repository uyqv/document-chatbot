
---

# Intelligent Document Assistant

## Overview

The Intelligent Document Assistant is a chatbot designed to provide users with information extracted from documents. It uses a combination of technologies including FastAPI for the backend, Elasticsearch for document indexing and retrieval, and React for the frontend interface. This assistant is capable of processing PDF documents, indexing their contents, and answering user queries by retrieving relevant information from the indexed documents.

## Features

- Chat interface for user queries with Markdown support for rich text responses.
- Backend API for handling chat sessions and user queries.
- Elasticsearch for indexing and retrieving document contents.
- Support for PDF document processing and indexing.
- Auto-scrolling chat view and loading indicators for a seamless user experience.

## Getting Started

### Prerequisites

- Python 3.7+
- Node.js and npm
- Elasticsearch service (local or cloud-based)

### Setup

1. **Backend Setup:**

    - Navigate to the backend directory.
    - Install required Python dependencies:

    ```bash
    pip install fastapi uvicorn elasticsearch langchain-openai
    ```

    - Start the FastAPI server (in backend/):

    ```bash
    uvicorn main:app --reload
    ```

2. **Elasticsearch Configuration:**

    - Ensure Elasticsearch is running and accessible.
    - Update `constants.py` with your Elasticsearch cloud ID, API key, and other relevant details.

3. **PDF Indexing:**

    - Run the provided Python script to index PDF documents into Elasticsearch:

    ```bash
    python ingest.py
    ```

4. **Frontend Setup:**

    - Navigate to the frontend directory.
    - Install required npm packages:

    ```bash
    npm install
    ```

    - Start the React development server (in frontend/chatbot-app/):

    ```bash
    npm start
    ```

### Usage

After setting up the backend, Elasticsearch, and frontend, you can start using the Intelligent Document Assistant by opening the React application in your browser. Type your queries into the chat interface, and the chatbot will respond with information retrieved from the indexed documents.

## Development

- **Backend Development:** The FastAPI backend can be extended by adding new endpoints or modifying the chatbot logic in `main.py`.
- **Frontend Development:** Modify the React application in the `src` directory to customize the user interface or add new features.
- **PDF Indexing:** Adjust the indexing script `index_pdf_folder.py` to change how documents are processed and indexed.

## Diagram

![inforeach_process_diagram.png](inforeach_process_diagram.png)

## License

Specify your project's license here.

---
