SynapseAI

Autonomous Multi-Agent Research & Learning Copilot powered by Hybrid RAG, Explainable AI, and Intelligent Agent Orchestration.

Overview

SynapseAI is an advanced AI-powered research and personalized learning platform designed to transform unstructured documents into interactive, explainable, and adaptive knowledge systems.

Unlike traditional PDF chatbots, SynapseAI combines:

Hybrid Retrieval-Augmented Generation (RAG)
Multi-Agent AI workflows
Explainable source lineage
Personalized learning orchestration
Interactive knowledge visualization

to create a production-grade AI learning assistant.

Users can upload:

Research papers
Lecture notes
Technical PDFs
Documentation

and interact with an intelligent AI system capable of:

answering contextual questions
generating summaries
creating quizzes
building study roadmaps
tracing exact source citations
orchestrating autonomous AI agents
Key Features
Intelligent PDF Ingestion
Drag-and-drop PDF upload system
Automatic text extraction using PyPDF2
Smart document chunking via LangChain
Embedding generation using SentenceTransformers
Vector storage using FAISS
Context-Aware AI Chat
Real-time conversational interface
Powered by Groq LLM APIs
Contextual document reasoning
Streaming AI responses
Explainable AI Lineage

SynapseAI dynamically cites:

document sources
chunk references
contextual passages

used to generate each answer.

This creates transparent and trustworthy AI outputs.

Hybrid Retrieval Pipeline (Phase 2)

Combines:

Dense vector similarity search
Sparse BM25 keyword retrieval

for improved retrieval precision and reduced hallucinations.

Multi-Agent AI Orchestration (Phase 2)

Autonomous specialized agents:

Planner Agent
Research Agent
Quiz Agent
Summarization Agent
Citation Agent

powered by LangGraph workflows.

Personalized Learning Engine (Phase 3)

Generates:

adaptive study roadmaps
weak-topic analysis
revision schedules
progress tracking

based on uploaded learning materials.

Interactive Knowledge Graph (Phase 3)

Visual graph-based representation of:

concepts
dependencies
relationships
prerequisite chains

using React Flow.

Tech Stack
Frontend
React.js
Vite
TailwindCSS
Framer Motion
React Flow
Recharts
Backend
FastAPI
LangChain
LangGraph
SentenceTransformers
PyPDF2
Vector Database
FAISS (Current MVP)
ChromaDB / pgvector (Planned)
AI Models
llama-3.3-70b-versatile
Groq API
System Architecture
User Uploads PDF
        ↓
Document Processing Pipeline
        ↓
Text Extraction
        ↓
Chunking & Embeddings
        ↓
Vector Storage
        ↓
Hybrid Retrieval Engine
        ↓
Multi-Agent Orchestrator
        ↓
LLM Response Generation
        ↓
Explainable Citation Mapping
        ↓
Frontend Visualization
Project Structure
SynapseAI/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── animations/
│   │   ├── graphs/
│   │   └── chat/
│   └── public/
│
├── backend/
│   ├── agents/
│   ├── rag/
│   ├── embeddings/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── vector_db/
│
├── docs/
│
└── README.md
Current MVP Features
Completed
PDF upload pipeline
RAG-based contextual chat
FAISS vector search
Explainable source citations
Animated modern UI
FastAPI backend
Groq LLM integration
Upcoming Features
Phase 2
Hybrid Retrieval (BM25 + Dense Search)
LangGraph Multi-Agent Orchestration
Planner Agent
Streaming responses
Phase 3
Knowledge Graph Visualization
Quiz & Flashcard Generator
Personalized Learning Paths
Analytics Dashboard
Phase 4
Authentication & User Profiles
Long-term Conversation Memory
Multi-document Comparison
Voice AI Support
Installation
Clone Repository
git clone https://github.com/your-username/SynapseAI.git
cd SynapseAI
Backend Setup
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

Create a .env file:

GROQ_API_KEY=your_api_key

Run backend:

uvicorn main:app --reload

Backend runs on:

http://localhost:8000
Frontend Setup
cd frontend

npm install

npm run dev

Frontend runs on:

http://localhost:5173
API Endpoints
Upload Documents
POST /upload

Uploads and processes PDF files into vector embeddings.

Chat Endpoint
POST /chat

Executes RAG pipeline and returns contextual AI responses.

Resume-Worthy Highlights
Built a production-grade AI research assistant using Hybrid RAG pipelines and multi-agent orchestration.
Implemented explainable AI lineage tracking for transparent source attribution.
Developed scalable FastAPI backend integrated with vector search and LLM inference.
Engineered responsive React frontend with modern glassmorphic UI/UX.
Designed autonomous AI agent workflows using LangGraph.
Future Scope

SynapseAI can evolve into:

Enterprise knowledge assistant
Research paper copilot
AI tutoring platform
Technical interview preparation system
Academic learning ecosystem
