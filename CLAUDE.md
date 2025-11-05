# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Novel RAG Analysis System** (小说RAG分析系统) - a Chinese novel intelligent analysis platform based on RAG (Retrieval Augmented Generation) technology. The system consists of:

- **Frontend**: React + TypeScript + Vite web application for user interface
- **Backend**: FastAPI + Python backend with LangChain and Zhipu AI integration
- **Core Features**: Novel management, intelligent search & Q&A, character relationship graphs, chapter reading

## Architecture

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/          # Main pages (SearchPage, GraphPage, ReaderPage)
│   ├── components/     # Reusable components
│   ├── store/         # Zustand state management
│   ├── types/         # TypeScript type definitions
│   ├── utils/         # Utility functions (db.ts, textProcessing.ts)
│   └── main.tsx       # Application entry
├── public/            # Static assets
├── package.json       # Dependencies and scripts
└── vite.config.ts     # Vite configuration
```

### Backend Structure (Planned)
```
backend/
├── app/
│   ├── api/          # API routes (auth, novels, search, graph)
│   ├── services/     # Business logic (RAGService, TextProcessingService)
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── tasks/        # Celery async tasks
├── pyproject.toml    # Poetry dependencies
└── docker-compose.yml # Database services
```

## Development Commands

### Frontend (React + Vite)
```bash
cd frontend

# Install dependencies
npm install

# Development server (starts at http://localhost:5173)
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Preview production build
npm run preview
```

### Backend (Python + FastAPI) - Planned
```bash
cd backend

# Install dependencies with Poetry
poetry install

# Start development server
poetry run uvicorn app.main:app --reload --port 8000

# Run database migrations
poetry run alembic upgrade head

# Start Celery worker
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

### Infrastructure Services
```bash
# Start all services (MySQL, Redis, Qdrant)
docker-compose up -d

# Check service status
docker-compose ps

# Stop services
docker-compose down
```

## Core Technologies

### Frontend Stack
- **React 19.1.1** + **TypeScript 5.9.3** - Main framework
- **Vite 7.1.7** - Build tool and dev server
- **Ant Design 5.28.0** - UI component library
- **Zustand 5.0.8** - State management
- **React Router 7.9.5** - Navigation
- **Dexie.js 4.2.1** - IndexedDB wrapper for local storage
- **React Force Graph 2D** - Character relationship visualization

### Backend Stack (Planned)
- **FastAPI** - Web framework
- **LangChain** + **LangGraph** - RAG framework
- **Zhipu AI GLM-4** - Chinese LLM for Q&A
- **Qdrant** - Vector database for embeddings
- **MySQL** - Primary database
- **Redis** - Cache and message queue
- **Celery** - Async task processing

## Key Features

### 1. Novel Management
- Support for TXT format Chinese novels
- Automatic encoding detection (UTF-8, GBK, GB2312)
- Chapter recognition and organization
- Local storage using IndexedDB

### 2. Intelligent Search & Q&A
- Natural language question input
- Semantic search using embeddings
- Context-aware answer generation
- Reference text citations

### 3. Character Relationship Graphs
- Automatic character extraction
- Relationship type identification
- Interactive force-directed visualization
- Graph export functionality

### 4. Chapter Reader
- Chapter navigation
- Reading progress tracking
- Customizable reading themes
- Text highlighting and search

## Data Models

### Novel
```typescript
interface Novel {
  id: string;
  title: string;
  author?: string;
  description?: string;
  tags: string[];
  content: string;
  chapters: Chapter[];
  wordCount: number;
  importedAt: number;
}
```

### Chapter
```typescript
interface Chapter {
  id: string;
  novelId: string;
  chapterNumber: number;
  title: string;
  startPosition: number;
  endPosition: number;
  wordCount: number;
}
```

### Character Graph
```typescript
interface CharacterGraph {
  id: string;
  novelId: string;
  characters: Character[];
  relationships: Relationship[];
  generatedAt: number;
}
```

## Important Notes

### Current Implementation Status
- ✅ **Frontend MVP**: Complete with mock data
- ✅ **Local Storage**: IndexedDB for offline functionality
- ⏳ **Backend Integration**: API endpoints defined but not implemented
- ⏳ **RAG Pipeline**: Technical specification ready

### File Encoding Handling
The system specifically handles Chinese text encoding:
- Automatic detection using `chardet` library
- Support for UTF-8, GBK, GB2312 encodings
- Character validation (minimum 60% Chinese content)

### Performance Considerations
- Large file support (up to 300万字/3M characters)
- Chunked text processing for memory efficiency
- Virtual scrolling for long lists
- IndexedDB for persistent local storage

### Mock Data Usage
Frontend currently uses mock data to demonstrate functionality:
- Search results are simulated
- Character relationships are randomly generated
- API calls are mocked with realistic delays

## Development Workflow

### Adding New Features
1. Define TypeScript interfaces in `src/types/`
2. Create UI components in `src/components/`
3. Update Zustand store in `src/store/`
4. Add utility functions in `src/utils/`
5. Test with mock data before backend integration

### Backend Integration
When backend is ready:
1. Replace mock data with real API calls
2. Update error handling for network requests
3. Add loading states and user feedback
4. Implement authentication flow

### Testing
```bash
# Frontend linting
cd frontend && npm run lint

# Backend testing (when implemented)
cd backend && poetry run pytest
```

## Environment Setup

### Prerequisites
- Node.js 18+ for frontend development
- Python 3.10+ for backend development
- Docker for database services
- Zhipu AI API key for RAG functionality

### Configuration Files
- `frontend/package.json` - Frontend dependencies and scripts
- `backend/pyproject.toml` - Backend Python dependencies
- `docker-compose.yml` - Infrastructure services
- `.env` - Environment variables (API keys, database URLs)

## API Integration

### Backend API Specification
See `backend_api_specification.yaml` for complete API documentation including:
- Authentication endpoints
- Novel management CRUD operations
- Text processing and upload
- RAG search and Q&A
- Character relationship graph generation

### Frontend-Backend Communication
- HTTP client using `fetch` API
- JWT authentication
- Error handling and user feedback
- Request/response type safety with TypeScript

## Deployment

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy dist/ folder to web server
```

### Backend Deployment
```bash
cd backend
poetry install
docker-compose up -d
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Common Issues
1. **Large file imports**: Use chunked processing and show progress indicators
2. **Encoding detection**: Fallback to manual selection if auto-detection fails
3. **Storage limits**: Monitor IndexedDB usage and implement cleanup strategies
4. **Performance**: Implement virtualization for large datasets

### Debugging Tools
- Browser DevTools for IndexedDB inspection
- React DevTools for component state
- Network tab for API monitoring
- Console for error tracking