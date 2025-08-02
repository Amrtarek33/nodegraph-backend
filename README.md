# NodeGraph Backend

A high-performance Django REST API for managing graph-based node connections with advanced pathfinding capabilities.

## 🚀 Features

- **Graph Management**: Create, connect, and manage nodes in a graph structure
- **Path Finding**: Find optimal paths between nodes
- **Async Processing**: Background task processing with Celery
- **RESTful API**: Clean, documented REST endpoints


## 📋 Prerequisites
- Python 3.8+
- Redis (for caching and Celery)
- Virtual environment

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nodegraph-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   Create a `.env` file in the project root:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (SQLite for development)
   DEFAULT_DB_ENGINE=django.db.backends.sqlite3
   DEFAULT_DB_NAME=db.sqlite3
   
   
   # Redis/Celery
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   
   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Redis** (required for caching and Celery)
   ```bash
   # On Ubuntu/Debian
   sudo systemctl start redis
   
   # On macOS with Homebrew
   brew services start redis
   
   # Or run directly
   redis-server
   ```

## 🚀 Running the Application

### Development Server
```bash
# Start Django development server
python manage.py runserver

# Start Celery worker (in a separate terminal)
celery -A nodeproject worker --loglevel=info

```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### 1. Create Node
```http
POST /api/create-node/
Content-Type: application/json

{
    "name": "NodeA"
}
```

#### 2. Connect Nodes
```http
POST /api/connect-nodes/
Content-Type: application/json

{
    "FromNode": "NodeA",
    "ToNode": "NodeB"
}
```

#### 3. Find Path
```http
GET /api/find-path/?FromNode=NodeA&ToNode=NodeB
```

#### 4. Slow Path Finding (Async)
```http
POST /api/slow-find-path/
Content-Type: application/json

{
    "FromNode": "NodeA",
    "ToNode": "NodeB"
}
```

#### 5. Get Async Task Result
```http
GET /api/get-slow-path-result/?task_id=<task_id>
```

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

The application includes comprehensive tests covering:
- Node creation and management
- Connection operations
- Path finding algorithms
- Async task processing
- Error handling scenarios

