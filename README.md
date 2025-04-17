# Vector Search API Demo

This is a demo API that performs semantic search on a product catalog using vector embeddings.

## API Endpoint

The API exposes a single endpoint for semantic search:

```
POST /search
```

### Request Format
```json
{
    "query": "your search query here"
}
```

### Example Usage

Using curl:
```bash
curl -X POST "https://your-deployed-url/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "comfortable headphones for travel"}'
```

Using Python requests:
```python
import requests

response = requests.post(
    "https://your-deployed-url/search",
    json={"query": "comfortable headphones for travel"}
)
print(response.json())
```

### Response Format
```json
{
    "closest_match": {
        "id": 1,
        "name": "Wireless Noise-Canceling Headphones",
        "description": "Immerse yourself in pure audio with these comfortable and powerful headphones. Perfect for travel and focused work.",
        "score": 0.89
    },
    "other_nearest_matches": [
        {
            "id": 6,
            "name": "Portable Bluetooth Speaker",
            "description": "Enjoy your favorite music anywhere with this compact and water-resistant Bluetooth speaker.",
            "score": 0.75
        },
        // ... more matches
    ]
}
```

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python practice.py
```

The server will start at `http://localhost:8000` 