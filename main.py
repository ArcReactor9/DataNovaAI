from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.models import DatasetMetadata, Transaction
from core.data_manager import DataManager
from blockchain.solana_client import SolanaClient
from ai_agent.research_agent import ResearchAssistant
from typing import List, Optional
import uvicorn
import os
from datetime import datetime

app = FastAPI(title="DataNovaAI API")
data_manager = DataManager()
solana_client = SolanaClient()
research_assistant = ResearchAssistant()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/dataset/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    metadata: DatasetMetadata = None
):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store dataset and metadata
        dataset_id = data_manager.store_dataset(temp_path, metadata)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return {"dataset_id": dataset_id, "message": "Dataset uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dataset/{dataset_id}")
async def get_dataset(dataset_id: str):
    try:
        data, metadata = data_manager.retrieve_dataset(dataset_id)
        return {
            "metadata": metadata,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {str(e)}")

@app.post("/dataset/purchase")
async def purchase_dataset(transaction: Transaction):
    try:
        # Verify buyer has sufficient funds
        buyer_balance = solana_client.get_balance(transaction.buyer_address)
        if buyer_balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Process transaction on Solana blockchain
        tx_signature = solana_client.transfer_tokens(
            transaction.buyer_address,
            transaction.seller_address,
            transaction.amount
        )
        
        if not tx_signature:
            raise HTTPException(status_code=500, detail="Transaction failed")
        
        # Record transaction
        transaction.transaction_id = tx_signature
        transaction.timestamp = datetime.now()
        transaction.status = "completed"
        data_manager.record_transaction(transaction)
        
        return {"transaction_id": tx_signature, "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/analyze")
async def analyze_dataset(dataset_id: str, query: str):
    try:
        # Retrieve dataset
        data, metadata = data_manager.retrieve_dataset(dataset_id)
        
        # Process research query
        results = research_assistant.process_research_query(
            query,
            context={"dataset": data, "metadata": metadata}
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets(
    data_type: Optional[str] = None,
    author: Optional[str] = None
):
    filters = {}
    if data_type:
        filters["data_type"] = data_type
    if author:
        filters["authors"] = author
    
    datasets = data_manager.list_datasets(filters)
    return datasets

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
