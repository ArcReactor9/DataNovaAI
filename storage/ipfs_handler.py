import ipfshttpclient
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime

class IPFSHandler:
    def __init__(self):
        self.client = ipfshttpclient.connect()
        self.pin_list = {}
    
    def add_file(self, file_path: str) -> Dict[str, Any]:
        """Add a file to IPFS and return its hash"""
        try:
            result = self.client.add(file_path)
            file_hash = result['Hash']
            
            # Pin the file to ensure persistence
            self.client.pin.add(file_hash)
            self.pin_list[file_hash] = {
                'timestamp': datetime.utcnow().isoformat(),
                'path': file_path
            }
            
            return {
                'hash': file_hash,
                'size': result['Size'],
                'name': os.path.basename(file_path)
            }
        except Exception as e:
            raise Exception(f"Error adding file to IPFS: {str(e)}")
    
    def get_file(self, ipfs_hash: str, output_path: str) -> bool:
        """Retrieve a file from IPFS by its hash"""
        try:
            self.client.get(ipfs_hash, output_path)
            return True
        except Exception as e:
            raise Exception(f"Error retrieving file from IPFS: {str(e)}")
    
    def pin_file(self, ipfs_hash: str) -> bool:
        """Pin a file to ensure it persists in the network"""
        try:
            self.client.pin.add(ipfs_hash)
            return True
        except Exception as e:
            raise Exception(f"Error pinning file: {str(e)}")
    
    def unpin_file(self, ipfs_hash: str) -> bool:
        """Unpin a file if it's no longer needed"""
        try:
            self.client.pin.rm(ipfs_hash)
            if ipfs_hash in self.pin_list:
                del self.pin_list[ipfs_hash]
            return True
        except Exception as e:
            raise Exception(f"Error unpinning file: {str(e)}")
    
    def list_pins(self) -> Dict[str, Any]:
        """List all pinned files"""
        return self.pin_list
    
    def add_directory(self, dir_path: str) -> Dict[str, Any]:
        """Add an entire directory to IPFS"""
        try:
            result = self.client.add(dir_path, recursive=True)
            dir_hash = result[-1]['Hash']  # Last item contains the directory hash
            
            # Pin the directory
            self.client.pin.add(dir_hash)
            self.pin_list[dir_hash] = {
                'timestamp': datetime.utcnow().isoformat(),
                'path': dir_path,
                'type': 'directory'
            }
            
            return {
                'hash': dir_hash,
                'size': result[-1]['Size'],
                'name': os.path.basename(dir_path)
            }
        except Exception as e:
            raise Exception(f"Error adding directory to IPFS: {str(e)}")
    
    def get_directory(self, ipfs_hash: str, output_path: str) -> bool:
        """Retrieve an entire directory from IPFS"""
        try:
            self.client.get(ipfs_hash, output_path)
            return True
        except Exception as e:
            raise Exception(f"Error retrieving directory from IPFS: {str(e)}")
    
    def close(self):
        """Close the IPFS client connection"""
        try:
            self.client.close()
        except:
            pass
