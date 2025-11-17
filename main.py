import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Whiteningproduct, Order, Subscriber

app = FastAPI(title="Teeth Whitening Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility: convert Mongo doc to JSON-safe dict

def _normalize(doc: dict):
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Convert any nested ObjectIds if present in simple structures
    return d


@app.get("/")
def read_root():
    return {"message": "Teeth Whitening Store Backend Running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


@app.get("/api/products")
def list_products() -> List[dict]:
    # Fetch products; if none, seed a default product for convenience
    products = get_documents("whiteningproduct")
    if not products:
        sample = Whiteningproduct(
            title="Pro Whitening Strips",
            subtitle="Powerful, enamel-safe whitening in 14 days",
            description=(
                "Clinically proven to remove years of stains with zero sensitivity. "
                "Mint-fresh strips that mold to your smile."
            ),
            price=29.0,
            compare_at_price=39.0,
            image="https://images.unsplash.com/photo-1605497787939-b4d9f29c67a2?w=1200&q=80&auto=format&fit=crop",
            gallery=[
                "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1200&q=80&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1598096969067-3ebbefdf2901?w=1200&q=80&auto=format&fit=crop",
            ],
            badges=["Enamel-safe", "No sensitivity", "Vegan"],
            in_stock=True,
        )
        create_document("whiteningproduct", sample)
        products = get_documents("whiteningproduct")
    return [_normalize(p) for p in products]


@app.post("/api/orders")
def create_order(order: Order):
    # Basic validation: items present and total >= subtotal
    if not order.items or order.total < order.subtotal:
        raise HTTPException(status_code=400, detail="Invalid order totals or items")
    inserted_id = create_document("order", order)
    return {"id": inserted_id, "status": "received"}


@app.post("/api/subscribe")
def subscribe(subscriber: Subscriber):
    # Idempotent-like behavior: allow duplicates but that's fine for demo
    inserted_id = create_document("subscriber", subscriber)
    return {"id": inserted_id, "status": "subscribed"}


class SchemaInfo(BaseModel):
    name: str
    fields: dict


@app.get("/schema")
def get_schema():
    # Minimal schema info for viewers/tools
    return {
        "whiteningproduct": list(Whiteningproduct.model_json_schema()["properties"].keys()),
        "order": list(Order.model_json_schema()["properties"].keys()),
        "subscriber": list(Subscriber.model_json_schema()["properties"].keys()),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
