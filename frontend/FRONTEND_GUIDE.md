# Frontend Integration Guide

## Quick Start - HTML/JavaScript (Included)

The simplest way to test the frontend is to use the included `index.html`:

1. **Start the API server:**
   ```bash
   uvicorn api:app --reload
   ```

2. **Open the frontend:**
   - Simply double-click `frontend/index.html` in File Explorer
   - Or open it in your browser: `file:///path/to/frontend/index.html`

3. **Start searching!**
   - The frontend will connect to `http://127.0.0.1:8000`

---

## React Integration

### Create React App Example

```jsx
// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [query, setQuery] = useState('');
  const [store, setStore] = useState('my-docs');
  const [stores, setStores] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load stores on mount
  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/stores`);
      const data = await response.json();
      setStores(data.stores);
    } catch (err) {
      setError('Failed to load stores');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          store_name: store,
          temperature: 0.0,
          max_tokens: 1024
        })
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔍 RAG Search System</h1>
      </header>

      <main className="container">
        <form onSubmit={handleSearch}>
          <div className="search-box">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question..."
              disabled={loading}
            />
            
            <select value={store} onChange={(e) => setStore(e.target.value)}>
              {stores.map(s => (
                <option key={s.id} value={s.display_name}>
                  {s.display_name}
                </option>
              ))}
            </select>

            <button type="submit" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <div className="answer-box">
              <h3>Answer</h3>
              <p>{result.answer}</p>
            </div>

            {result.citations.length > 0 && (
              <div className="citations">
                <h3>Sources ({result.citations.length})</h3>
                {result.citations.map((cite, idx) => (
                  <div key={idx} className="citation">
                    <strong>{cite.file_name}</strong>
                    <p>{cite.chunk_text.substring(0, 200)}...</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
```

### Setup React Project

```bash
# Create new React app
npx create-react-app rag-frontend
cd rag-frontend

# Install axios (optional, for easier API calls)
npm install axios

# Copy the App.js above to src/App.js

# Start development server
npm start
```

---

## Vue.js Integration

```vue
<!-- src/App.vue -->
<template>
  <div id="app">
    <header>
      <h1>🔍 RAG Search System</h1>
    </header>

    <main class="container">
      <div class="search-box">
        <input
          v-model="query"
          @keyup.enter="searchDocuments"
          placeholder="Ask a question..."
          :disabled="loading"
        />
        
        <select v-model="selectedStore">
          <option v-for="store in stores" :key="store.id" :value="store.display_name">
            {{ store.display_name }}
          </option>
        </select>

        <button @click="searchDocuments" :disabled="loading">
          {{ loading ? 'Searching...' : 'Search' }}
        </button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="result" class="result">
        <div class="answer-box">
          <h3>Answer</h3>
          <p>{{ result.answer }}</p>
        </div>

        <div v-if="result.citations.length > 0" class="citations">
          <h3>Sources ({{ result.citations.length }})</h3>
          <div v-for="(cite, idx) in result.citations" :key="idx" class="citation">
            <strong>{{ cite.file_name }}</strong>
            <p>{{ cite.chunk_text.substring(0, 200) }}...</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export default {
  name: 'App',
  data() {
    return {
      query: '',
      selectedStore: 'my-docs',
      stores: [],
      result: null,
      loading: false,
      error: ''
    };
  },
  mounted() {
    this.loadStores();
  },
  methods: {
    async loadStores() {
      try {
        const response = await axios.get(`${API_BASE}/api/stores`);
        this.stores = response.data.stores;
      } catch (err) {
        this.error = 'Failed to load stores';
      }
    },
    async searchDocuments() {
      if (!this.query.trim()) return;

      this.loading = true;
      this.error = '';
      this.result = null;

      try {
        const response = await axios.post(`${API_BASE}/api/search`, {
          query: this.query,
          store_name: this.selectedStore,
          temperature: 0.0,
          max_tokens: 1024
        });

        this.result = response.data;
      } catch (err) {
        this.error = 'Search failed: ' + err.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## Flutter/Dart Integration

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';

  Future<Map<String, dynamic>> search(String query, String storeName) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/search'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'query': query,
        'store_name': storeName,
        'temperature': 0.0,
        'max_tokens': 1024
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Search failed');
    }
  }

  Future<List<dynamic>> getStores() async {
    final response = await http.get(Uri.parse('$baseUrl/api/stores'));
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['stores'];
    } else {
      throw Exception('Failed to load stores');
    }
  }
}
```

---

## Next.js Integration

```javascript
// pages/index.js
import { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000';

export default function Home() {
  const [query, setQuery] = useState('');
  const [stores, setStores] = useState([]);
  const [selectedStore, setSelectedStore] = useState('my-docs');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/stores`)
      .then(res => res.json())
      .then(data => setStores(data.stores));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);

    const response = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        store_name: selectedStore,
        temperature: 0.0,
        max_tokens: 1024
      })
    });

    const data = await response.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <div>
      <h1>RAG Search System</h1>
      <form onSubmit={handleSearch}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question..."
        />
        <select value={selectedStore} onChange={(e) => setSelectedStore(e.target.value)}>
          {stores.map(s => (
            <option key={s.id} value={s.display_name}>{s.display_name}</option>
          ))}
        </select>
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {result && (
        <div>
          <h3>Answer</h3>
          <p>{result.answer}</p>
          <h3>Sources ({result.citations.length})</h3>
          {result.citations.map((cite, i) => (
            <div key={i}>
              <strong>{cite.file_name}</strong>
              <p>{cite.chunk_text.substring(0, 200)}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## CORS Configuration (Important!)

If you get CORS errors, the API is already configured to allow all origins:

```python
# In api.py (already set)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, change to specific origins:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

---

## Testing the Connection

1. **Start API:** `uvicorn api:app --reload`
2. **Open frontend:** `frontend/index.html`
3. **Test search:** Enter a query and click Search
4. **Check browser console** for any errors (F12)

---

## Deployment Options

### Deploy Backend (FastAPI)
- **Railway**: `railway up`
- **Heroku**: `git push heroku main`
- **AWS/Azure**: Use Docker container
- **Vercel**: Deploy as serverless function

### Deploy Frontend
- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy`
- **GitHub Pages**: For static HTML
- **Firebase Hosting**: `firebase deploy`

---

## Mobile App Integration

For mobile apps (React Native, Flutter), use the same API endpoints:

```javascript
// React Native
const response = await fetch('http://YOUR_API_URL:8000/api/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query, store_name: 'my-docs' })
});
```

**Note:** Replace `127.0.0.1` with your server's IP address or domain when deploying!
