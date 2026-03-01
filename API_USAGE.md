# FastAPI Endpoints Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Interactive API Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## Available Endpoints

### 1. Health Check
```bash
GET /health
```

**cURL Example:**
```bash
curl http://127.0.0.1:8000/health
```

---

### 2. Search Documents
```bash
POST /api/search
```

**Request Body:**
```json
{
  "query": "What are the key findings?",
  "store_name": "my-docs",
  "temperature": 0.0,
  "max_tokens": 1024
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/search" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What are ICAR findings?\", \"store_name\": \"my-docs\"}"
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/search",
    json={
        "query": "What are the key findings?",
        "store_name": "my-docs"
    }
)
print(response.json())
```

---

### 3. List All Stores
```bash
GET /api/stores
```

**cURL Example:**
```bash
curl http://127.0.0.1:8000/api/stores
```

**Python Example:**
```python
import requests

response = requests.get("http://127.0.0.1:8000/api/stores")
stores = response.json()
print(stores)
```

---

### 4. Create New Store
```bash
POST /api/stores
```

**Request Body:**
```json
{
  "store_name": "new-store"
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/stores" \
  -H "Content-Type: application/json" \
  -d "{\"store_name\": \"new-store\"}"
```

---

### 5. Upload File
```bash
POST /api/upload
```

**Form Data:**
- `file`: File to upload
- `store_name`: Store name

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/upload" \
  -F "file=@document.pdf" \
  -F "store_name=my-docs"
```

**Python Example:**
```python
import requests

files = {'file': open('document.pdf', 'rb')}
data = {'store_name': 'my-docs'}

response = requests.post(
    "http://127.0.0.1:8000/api/upload",
    files=files,
    data=data
)
print(response.json())
```

---

### 6. Generate Summary
```bash
POST /api/summarize
```

**Request Body:**
```json
{
  "store_name": "my-docs"
}
```

**cURL Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/summarize" \
  -H "Content-Type: application/json" \
  -d "{\"store_name\": \"my-docs\"}"
```

---

### 7. Delete Store
```bash
DELETE /api/stores/{store_name}
```

**cURL Example:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/stores/my-docs"
```

---

## JavaScript/Frontend Integration

### Fetch API Example:
```javascript
// Search documents
async function searchDocuments(query) {
  const response = await fetch('http://127.0.0.1:8000/api/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      store_name: 'my-docs',
      temperature: 0.0,
      max_tokens: 1024
    })
  });
  
  const data = await response.json();
  return data;
}

// Usage
searchDocuments("What are the key findings?")
  .then(result => {
    console.log("Answer:", result.answer);
    console.log("Citations:", result.citations);
  });
```

### Axios Example:
```javascript
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

// Search
const searchResponse = await axios.post(`${API_BASE}/api/search`, {
  query: "What are the findings?",
  store_name: "my-docs"
});

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('store_name', 'my-docs');

const uploadResponse = await axios.post(`${API_BASE}/api/upload`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
```

---

## React Example Component

```jsx
import React, { useState } from 'react';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          store_name: 'my-docs'
        })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      {result && (
        <div>
          <h3>Answer:</h3>
          <p>{result.answer}</p>
          <h4>Sources: {result.citations.length}</h4>
        </div>
      )}
    </div>
  );
}
```

---

## Testing with Postman

1. Import the API into Postman
2. Set base URL: `http://127.0.0.1:8000`
3. Test endpoints with the examples above

---

## Running the Server

```bash
# Start server
uvicorn api:app --reload

# Start on different port
uvicorn api:app --reload --port 8080

# Start with host binding
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

---

## CORS Configuration

The API is configured to accept requests from any origin (`*`). For production, update in `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
