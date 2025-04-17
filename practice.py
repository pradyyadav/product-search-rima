from fastapi import FastAPI
from qdrant_client import QdrantClient, models
from fastembed import TextEmbedding
import uvicorn
import json
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Vector Search API",
    description="A semantic search API for product catalog using vector embeddings",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

embedding_model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = QdrantClient(":memory:")


class SearchQuery(BaseModel):
    query: str


class PointStruct(BaseModel):
    id: int
    name: str
    description: str
    score: float


class ProductResponse(BaseModel):
    closest_match: PointStruct
    other_nearest_matches: list[PointStruct]


def load_products():
    products = [
        {
            "id": 1,
            "name": "Wireless Noise-Canceling Headphones",
            "description": "Immerse yourself in pure audio with these comfortable and powerful headphones. Perfect for travel and focused work.",
        },
        {
            "id": 2,
            "name": "Ergonomic Office Chair",
            "description": "Designed for all-day comfort and support, this chair helps improve posture and reduce back pain.",
        },
        {
            "id": 3,
            "name": "Smart Coffee Maker with Voice Control",
            "description": "Start your day right with a freshly brewed cup of coffee, controlled by your voice or a mobile app.",
        },
        {
            "id": 4,
            "name": "Lightweight Running Shoes",
            "description": "Engineered for speed and agility, these shoes provide excellent cushioning for your daily runs.",
        },
        {
            "id": 5,
            "name": "Bamboo Cutting Board Set",
            "description": "A durable and eco-friendly set of cutting boards for all your food preparation needs.",
        },
        {
            "id": 6,
            "name": "Portable Bluetooth Speaker",
            "description": "Enjoy your favorite music anywhere with this compact and water-resistant Bluetooth speaker.",
        },
    ]
    return products


def initialize_vector_store():
    """Initialize the vector store with products"""
    # Recreate collection
    client.recreate_collection(
        collection_name="Shopping",
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )

    # Load and process products
    products = load_products()
    descriptions = [product["description"] for product in products]

    # Generate embeddings
    embeddings = list(embedding_model.embed(descriptions))

    # Create points
    points = [
        models.PointStruct(
            id=product["id"],
            vector=embedding,
            payload=product,
        )
        for product, embedding in zip(products, embeddings)
    ]

    # Upsert points
    client.upsert(
        collection_name="Shopping",
        points=points,
    )


@app.post("/search", response_model=ProductResponse)
def get_query(search_query: SearchQuery):
    query_embed = list(embedding_model.embed([search_query.query]))[0]
    response = client.query_points(
        collection_name="Shopping",
        query=query_embed,
        limit=5,
    )

    # Get the first point (best match)
    first_point = response.points[0].payload

    return ProductResponse(
        closest_match=PointStruct(
            id=first_point["id"],
            name=first_point["name"],
            description=first_point["description"],
            score=response.points[0].score,
        ),
        other_nearest_matches=[
            PointStruct(
                id=point.id,
                name=point.payload["name"],
                description=point.payload["description"],
                score=point.score,
            )
            for point in response.points[1:]
        ],
    )


@app.on_event("startup")
async def startup_event():
    initialize_vector_store()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
