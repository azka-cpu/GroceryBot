# GroceryBot:
**Smart AI-powered grocery receipt analyzer using LangGraph + Streamlit**
## Overview:
GroceryBot is a full-stack AI application that automatically extracts, analyzes, and tracks grocery expenses from receipt images. Using Groq's vision AI and LangGraph's agentic workflows, GroceryBot provides real-time spending analytics and intelligent chat assistance.
## Features:
### Frontend
- **Streamlit** - Interactive UI framework
- **Python 3.8+** - Core language
### Backend
- **FastAPI** - High-performance REST API
- **LangGraph** - AI agent orchestration (ReAct pattern)
- **SQLAlchemy/SQLModel** - ORM for database operations
- **Pydantic** - Data validation
### AI & LLM
- **Groq LLMs** - llama-3.3-70b-versatile
- **Groq Vision API** - Receipt image OCR and analysis
- **LangChain** - LLM framework integration
### Database & Infrastructure
- **PostgreSQL** - Primary database (Supabase)
- **Streamlit Cloud** - Frontend hosting
  ## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Groq API key
- Git
### Setup
1. **Clone the repository**
```bash
git clone https://github.com/azka-cpu/GroceryBot.git
cd GroceryBot
```
2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Configure environment variables**
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:password@localhost/grocerybot
JWT_SECRET_KEY=your_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```
### Run Backend
```bash
cd app
uvicorn main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`
### Run Frontend
```bash
streamlit run frontend/streamlit_app.py
```
Frontend will be available at `http://localhost:8501`
## API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and get JWT token
### Slips (Receipts)
- `GET /slips` - Get all user receipts
- `POST /slips/upload` - Upload and process receipt image
- `DELETE /slips/{slip_id}` - Delete a receipt
### Chat
- `POST /chat` - Send message to AI assistant
- `GET /chat/history` - Get conversation history
## Key Components
### Receipt Parser (`slips/slip_parser.py`)
Processes receipt images using Groq Vision API to extract:
- Store name
- Date of purchase
- Item names and prices
- Total amount
- Payment method
### AI Agent (`chat/graph.py`)
LangGraph-based agent that:
- Understands spending queries in natural language
- Analyzes spending patterns
- Provides personalized recommendations
### Authentication System
- JWT token-based authentication
- Secure password hashing
- User session management
- CORS protection
**Performance Features**
- **Async Operations**: Non-blocking I/O for better scalability
- **Rate Limiting**: API throttling to prevent abuse
- **Caching**: Intelligent caching for frequent queries
- **Batch Processing**: Efficient bulk operations
- **Connection Pooling**: Optimized database connections
## Security
- Environment variable isolation (no `.env` in repo)
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration
- JWT token expiration
- Password hashing with bcrypt
## Deployment
### Streamlit Cloud (Frontend)
1. Connect GitHub repository
2. Select `frontend/streamlit_app.py`
3. Set environment variables
4. Deploy automatically on push
## License
This project is licensed under the MIT License - see LICENSE file for details.
## Support
For issues, questions, or suggestions:
- Open a GitHub issue
- Contact: azkalid842@gmail.com
## Author
**Axa** - AI Agent Developer
- GitHub: [@azka-cpu](https://github.com/azka-cpu)
- Location: Pakistan

