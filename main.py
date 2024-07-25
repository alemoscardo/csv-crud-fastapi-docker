from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

app = FastAPI()

csv_file_path = "data/records.csv"

class Record(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str

if not os.path.isfile(csv_file_path):
    df = pd.DataFrame(columns=["id", "nome", "cognome", "codice_fiscale"])
    df.to_csv(csv_file_path, index=False)

def read_csv():
    return pd.read_csv(csv_file_path)

def write_csv(df):
    df.to_csv(csv_file_path, index=False)

@app.post("/items/", response_model=Record)
def create_item(record: Record):
    df = read_csv()
    if record.id in df["id"].values:
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    df = pd.concat([df, pd.DataFrame([record.dict()])], ignore_index=True)

    write_csv(df)
    return record

@app.get("/items/", response_model=list[Record])
def get_items():
    df = read_csv()
    return df.to_dict(orient="records")

@app.get("/items/count")
def get_count():
    df = read_csv()
    return {"count": len(df)}


@app.get("/items/{id}", response_model=Record)
def get_item(id: int):
    df = read_csv()
    if id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Item not found")
    item = df[df["id"] == id].iloc[0].to_dict()
    return item

@app.put("/items/{id}", response_model=Record)
def update_item(id: int, record: Record):
    df = read_csv()
    if id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Item not found")
    df.loc[df["id"] == id, ["nome", "cognome", "codice_fiscale"]] = record.nome, record.cognome, record.codice_fiscale
    write_csv(df)
    return record

@app.delete("/items/{id}")
def delete_item(id: int):
    df = read_csv()
    if id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Item not found")
    df = df[df["id"] != id]
    write_csv(df)
    return {"message": "Item deleted successfully"}