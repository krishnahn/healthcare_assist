# Complete API Documentation for Postman Testing

## Base URL
```
http://127.0.0.1:8000
```

---

## 📋 API Endpoints Summary

| # | Endpoint | Method | Purpose |
|---|----------|--------|---------|
| 1 | `/` | GET | Root/Health check |
| 2 | `/health` | GET | Health status |
| 3 | `/api/search` | POST | Search documents and get AI answer |
| 4 | `/api/ask` | POST | Ask question (alias for search) |
| 5 | `/api/summarize` | POST | Summarize all documents in store |
| 6 | `/api/upload` | POST | Upload a single file |
| 7 | `/api/upload-directory` | POST | Upload directory of files |
| 8 | `/api/stores` | GET | List all stores |
| 9 | `/api/stores` | POST | Create new store |
| 10 | `/api/stores/{store_name}` | DELETE | Delete a store |
| 11 | `/api/store-info/{store_name}` | GET | Get store details |

---

## 📝 Detailed Endpoint Documentation

### 1. Root Endpoint
**GET** `/`

**Purpose:** Check if API is running

**Headers:** None required

**Response:**
```json
{
  "message": "RAG System API is running",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

### 2. Health Check
**GET** `/health`

**Purpose:** Check API health status

**Headers:** None required

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1733396234.567
}
```

---

### 3. Search Documents (MAIN ENDPOINT)
**POST** `/api/search`

**Purpose:** Search through documents and get AI-generated answer

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What are the key findings from ICAR reports?",
  "store_name": "my-docs",
  "temperature": 0.0,
  "max_tokens": 1024,
  "system_prompt": "You are a helpful assistant."
}
```

**Body Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | The question to ask |
| `store_name` | string | ✅ Yes | - | Name of the document store |
| `temperature` | float | ❌ No | 0.0 | Response randomness (0.0-1.0) |
| `max_tokens` | integer | ❌ No | 1024 | Maximum response length |
| `system_prompt` | string | ❌ No | null | Custom system instructions |

**Response:**
```json
{
  "answer": "The ICAR reports highlight several key findings including improvements in agricultural productivity, new research initiatives, and technological advancements in farming practices...",
  "citations": [
    {
      "file_name": "ICAR Annual Report 2023-24-english.pdf",
      "chunk_text": "The Indian Council of Agricultural Research (ICAR) has made significant strides...",
      "page_number": 15,
      "score": 0.95,
      "metadata": {}
    }
  ],
  "metadata": {
    "processing_time": 2.345,
    "query": "What are the key findings from ICAR reports?",
    "model": "gemini-2.5-flash",
    "grounding_chunks_count": 5
  }
}
```

---

### 4. Ask Question (Alias)
**POST** `/api/ask`

**Purpose:** Same as `/api/search` - alternative endpoint name

**Headers:**
```
Content-Type: application/json
```

**Request Body:** Same as `/api/search`

**Response:** Same as `/api/search`

---

### 5. Summarize Documents
**POST** `/api/summarize`

**Purpose:** Generate a summary of all documents in a store

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "store_name": "my-docs"
}
```

**Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `store_name` | string | ✅ Yes | Name of the document store |

**Response:**
```json
{
  "summary": "The documents contain information about agricultural research, farming practices, district information for Punjab, and various verified datasets...",
  "citations": [
    {
      "file_name": "ICAR Annual Report 2023-24-english.pdf",
      "chunk_text": "Summary content from document...",
      "page_number": 1,
      "score": 0.92,
      "metadata": {}
    }
  ],
  "metadata": {
    "grounding_chunks_count": 8
  }
}
```

---

### 6. Upload File
**POST** `/api/upload`

**Purpose:** Upload a single document to a store

**Headers:**
```
Content-Type: multipart/form-data
```

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ Yes | The file to upload (PDF, DOCX, TXT, etc.) |
| `store_name` | string | ✅ Yes | Name of the store to upload to |

**In Postman:**
1. Select Body → form-data
2. Add key `file` → Select "File" type → Choose file
3. Add key `store_name` → Select "Text" → Enter "my-docs"

**Response:**
```json
{
  "success": true,
  "file_id": "files/abc123xyz",
  "filename": "document.pdf",
  "message": "Successfully uploaded document.pdf"
}
```

---

### 7. Upload Directory
**POST** `/api/upload-directory`

**Purpose:** Upload all files from a local directory

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `directory_path` | string | ✅ Yes | Absolute path to directory |
| `store_name` | string | ✅ Yes | Name of the store |

**In Postman:**
1. Select Body → x-www-form-urlencoded
2. Add key `directory_path` → Value: `C:/path/to/documents`
3. Add key `store_name` → Value: `my-docs`

**Response:**
```json
{
  "success": true,
  "files_uploaded": 5,
  "message": "Successfully uploaded 5 files"
}
```

---

### 8. List All Stores
**GET** `/api/stores`

**Purpose:** Get list of all document stores

**Headers:** None required

**Response:**
```json
{
  "success": true,
  "count": 3,
  "stores": [
    {
      "id": "fileSearchStores/mydocs-123abc",
      "display_name": "my-docs",
      "name": "fileSearchStores/mydocs-123abc",
      "create_time": "2025-12-05T10:30:00Z",
      "update_time": "2025-12-05T14:20:00Z"
    },
    {
      "id": "fileSearchStores/teststore-456def",
      "display_name": "test-store",
      "name": "fileSearchStores/teststore-456def",
      "create_time": "2025-12-04T09:15:00Z",
      "update_time": "2025-12-04T09:15:00Z"
    }
  ]
}
```

---

### 9. Create Store
**POST** `/api/stores`

**Purpose:** Create a new document store

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "store_name": "new-store"
}
```

**Body Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `store_name` | string | ✅ Yes | Name for the new store |

**Response:**
```json
{
  "success": true,
  "store_id": "fileSearchStores/newstore-789ghi",
  "message": "Successfully created store 'new-store'"
}
```

---

### 10. Delete Store
**DELETE** `/api/stores/{store_name}`

**Purpose:** Delete a document store

**Headers:** None required

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `store_name` | string | ✅ Yes | Name of the store to delete |

**Example URL:**
```
http://127.0.0.1:8000/api/stores/my-docs
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully deleted store 'my-docs'"
}
```

---

### 11. Get Store Info
**GET** `/api/store-info/{store_name}`

**Purpose:** Get detailed information about a specific store

**Headers:** None required

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `store_name` | string | ✅ Yes | Name of the store |

**Example URL:**
```
http://127.0.0.1:8000/api/store-info/my-docs
```

**Response:**
```json
{
  "success": true,
  "store": {
    "id": "fileSearchStores/mydocs-123abc",
    "display_name": "my-docs",
    "name": "fileSearchStores/mydocs-123abc",
    "create_time": "2025-12-05T10:30:00Z",
    "update_time": "2025-12-05T14:20:00Z"
  }
}
```

---

## 🚀 Postman Collection Setup

### Step 1: Create New Collection
1. Open Postman
2. Click "New" → "Collection"
3. Name it "RAG System API"

### Step 2: Set Base URL Variable
1. Click on Collection → Variables
2. Add variable:
   - Variable: `base_url`
   - Initial Value: `http://127.0.0.1:8000`
   - Current Value: `http://127.0.0.1:8000`

### Step 3: Add Requests
For each endpoint above:
1. Click "Add Request"
2. Set method (GET/POST/DELETE)
3. Enter URL as: `{{base_url}}/endpoint`
4. Add headers and body as specified

---

## 🧪 Testing Workflow

### 1. Check API Status
```
GET {{base_url}}/health
```

### 2. List Available Stores
```
GET {{base_url}}/api/stores
```

### 3. Create a New Store (if needed)
```
POST {{base_url}}/api/stores
Body: {"store_name": "test-store"}
```

### 4. Upload a Document
```
POST {{base_url}}/api/upload
Form-data:
  - file: [Select file]
  - store_name: test-store
```

### 5. Search Documents
```
POST {{base_url}}/api/search
Body: {
  "query": "What information is available?",
  "store_name": "test-store"
}
```

### 6. Summarize Store
```
POST {{base_url}}/api/summarize
Body: {"store_name": "test-store"}
```

---

## ⚠️ Error Responses

All endpoints return standard error format:

**400 Bad Request:**
```json
{
  "detail": "Validation error message"
}
```

**404 Not Found:**
```json
{
  "detail": "Store 'xyz' not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Search failed: [error details]"
}
```

---

## 📦 Quick Import for Postman

You can also visit the auto-generated interactive docs:
- **Swagger UI:** http://127.0.0.1:8000/docs
- Click "Try it out" on any endpoint to test directly
- Export to Postman using the "Download" button

---

## 🔑 Environment Variables (Optional)

In Postman, you can create environments:

**Local Environment:**
- `base_url`: `http://127.0.0.1:8000`
- `store_name`: `my-docs`
- `default_query`: `What information is available?`

Then use in requests: `{{base_url}}/api/search`

---

## ✅ Ready to Test!

1. Start the API: `uvicorn api:app --reload`
2. Import requests into Postman
3. Test each endpoint following the workflow above
