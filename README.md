📄 Cohere PDF/Text RAG System

A full-stack Retrieval-Augmented Generation (RAG) app built with FastAPI, React, and Cohere, allowing users to upload text files and ask questions that get answered based on their notes.

🚀 Features
Backend (FastAPI + Cohere)
 - Upload text files directly through the frontend
 - Automatically embed each uploaded document using Cohere’s embed-english-v3.0 model
 - Store:
    - docs → raw text
    - emb → embedding vectors
    - file_names → original filenames
 - Answer user questions using:
    - Cosine similarity to find the most relevant document
    - Cohere command-a-03-2025 to generate the answer using that context
    - CORS enabled for React frontend
    - Fully asynchronous API endpoints

Frontend (React)
 - Clean UI using Tailwind-style CSS (or default styling if not configured)
 - File upload interface
 - Question input box
 - Displays:
    - Answer
    - Source file used
    - Handles loading states

🧠 How the AI Works (High-Level Explanation)
1. Embeddings
 - Every word is broken into tokens
 - Tokens map to rows of a 1024-dimensional embedding matrix
 - The model learns these vectors during training using gradient descent
 - Vectors that are semantically similar appear closer in space

2. RAG Retrieval
 - Each uploaded document is embedded once
 - Query is embedded
 - Compute cosine similarity between query vector and each doc vector
 - The most similar document becomes context for the LLM

3. Answer Generation
 - Cohere command-a-03-2025 receives:
 - Context (your notes)
 - The user's question
 - Generates the best possible answer

🛠 Technologies Used
Frontend
 - React
 - Axios
Backend
 - FastAPI
 - Cohere
 - NumPy

AI
 - Cohere embed-english-v3.0
 - Cohere command-a-03-2025
