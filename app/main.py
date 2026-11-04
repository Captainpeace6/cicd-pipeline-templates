"""Small inventory API used to exercise the pipelines in this repo."""

import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="inventory-api")

_STARTED = time.time()
_ITEMS: dict[int, "Item"] = {}


class ItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=0)


class Item(ItemIn):
    id: int


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    return {
        "version": os.getenv("APP_VERSION", "dev"),
        "commit": os.getenv("GIT_SHA", "unknown"),
        "uptime_seconds": round(time.time() - _STARTED, 1),
    }


@app.get("/items")
def list_items() -> list[Item]:
    return list(_ITEMS.values())


@app.post("/items", status_code=201)
def create_item(item: ItemIn) -> Item:
    new = Item(id=len(_ITEMS) + 1, **item.model_dump())
    _ITEMS[new.id] = new
    return new


@app.get("/items/{item_id}")
def get_item(item_id: int) -> Item:
    if item_id not in _ITEMS:
        raise HTTPException(status_code=404, detail="item not found")
    return _ITEMS[item_id]
