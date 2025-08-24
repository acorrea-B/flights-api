# flights-api

REST API built with FastAPI to search flight journeys with up to two flight events. It retrieves data from an external API and returns valid journeys filtered by date, origin, destination, and constraints like max 24h duration and 4h layover. Async, fast, and integration-ready.

## 📁 Project Structure

```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       ├── requests/
│       └── responses/
├── adapters/
├── services/
├── dtos/
├── models/
├── utils/
├── main.py
```

## 🚀 Local Development Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <project-name>
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the app
```bash
uvicorn app.main:app --reload
```

### 5. Access the docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Docker Support

### Build Docker image
```bash
docker build -t flight-image .
```

### Run Docker container
```bash
sudo docker run -d -p 8000:8000 --name flight-container flight-image
```

## ✅ Running Tests

```bash
python -m unittest discover -s tests
```

Make sure mocks and fixtures are properly configured for all test cases.

---

© 2025 flights-api
