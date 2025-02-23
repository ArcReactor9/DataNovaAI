import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from .models import DatasetMetadata, Transaction
import json
import os

class DataManager:
    def __init__(self, storage_path: str = "data/"):
        self.storage_path = storage_path
        self._ensure_storage_directory()
        
    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
        
    def store_dataset(self, file_path: str, metadata: DatasetMetadata) -> str:
        """Store a dataset with its metadata"""
        try:
            # Generate unique dataset ID
            dataset_id = self._generate_dataset_id(file_path)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            metadata.file_hash = file_hash
            
            # Store dataset file
            dataset_path = os.path.join(self.storage_path, f"{dataset_id}.data")
            with open(file_path, 'rb') as source_file:
                with open(dataset_path, 'wb') as dest_file:
                    dest_file.write(source_file.read())
            
            # Store metadata
            metadata_path = os.path.join(self.storage_path, f"{dataset_id}.meta")
            with open(metadata_path, 'w') as f:
                json.dump(metadata.dict(), f)
            
            return dataset_id
        except Exception as e:
            raise Exception(f"Error storing dataset: {str(e)}")
    
    def retrieve_dataset(self, dataset_id: str) -> tuple[bytes, DatasetMetadata]:
        """Retrieve a dataset and its metadata"""
        try:
            # Read dataset file
            dataset_path = os.path.join(self.storage_path, f"{dataset_id}.data")
            with open(dataset_path, 'rb') as f:
                data = f.read()
            
            # Read metadata
            metadata_path = os.path.join(self.storage_path, f"{dataset_id}.meta")
            with open(metadata_path, 'r') as f:
                metadata_dict = json.load(f)
                metadata = DatasetMetadata(**metadata_dict)
            
            return data, metadata
        except Exception as e:
            raise Exception(f"Error retrieving dataset: {str(e)}")
    
    def verify_dataset(self, dataset_id: str) -> bool:
        """Verify dataset integrity"""
        try:
            data, metadata = self.retrieve_dataset(dataset_id)
            calculated_hash = hashlib.sha256(data).hexdigest()
            return calculated_hash == metadata.file_hash
        except Exception:
            return False
    
    def list_datasets(self, filters: Optional[Dict] = None) -> List[DatasetMetadata]:
        """List available datasets with optional filtering"""
        datasets = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.meta'):
                with open(os.path.join(self.storage_path, filename), 'r') as f:
                    metadata_dict = json.load(f)
                    metadata = DatasetMetadata(**metadata_dict)
                    
                    if filters:
                        # Apply filters
                        matches = all(
                            getattr(metadata, key, None) == value 
                            for key, value in filters.items()
                        )
                        if matches:
                            datasets.append(metadata)
                    else:
                        datasets.append(metadata)
        
        return datasets
    
    def _generate_dataset_id(self, file_path: str) -> str:
        """Generate a unique dataset ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        return f"dataset_{timestamp}_{file_hash}"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def record_transaction(self, transaction: Transaction):
        """Record a dataset transaction"""
        transaction_path = os.path.join(self.storage_path, "transactions.json")
        
        try:
            # Load existing transactions
            if os.path.exists(transaction_path):
                with open(transaction_path, 'r') as f:
                    transactions = json.load(f)
            else:
                transactions = []
            
            # Add new transaction
            transactions.append(transaction.dict())
            
            # Save updated transactions
            with open(transaction_path, 'w') as f:
                json.dump(transactions, f)
        except Exception as e:
            raise Exception(f"Error recording transaction: {str(e)}")
