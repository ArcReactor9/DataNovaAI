from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.keypair import Keypair
import os
from dotenv import load_dotenv

load_dotenv()

class SolanaClient:
    def __init__(self):
        self.endpoint = os.getenv("SOLANA_ENDPOINT")
        self.client = Client(self.endpoint)
        
    def create_wallet(self) -> Keypair:
        """Create a new Solana wallet"""
        return Keypair()
    
    def get_balance(self, public_key: str) -> float:
        """Get wallet balance"""
        try:
            balance = self.client.get_balance(public_key)
            return balance['result']['value'] / 10**9  # Convert lamports to SOL
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0
    
    def transfer_tokens(self, from_keypair: Keypair, to_address: str, amount: float) -> str:
        """Transfer tokens between wallets"""
        try:
            # Convert SOL to lamports
            amount_lamports = int(amount * 10**9)
            
            # Create transfer transaction
            transfer_params = TransferParams(
                from_pubkey=from_keypair.public_key,
                to_pubkey=to_address,
                lamports=amount_lamports
            )
            
            transaction = Transaction().add(transfer(transfer_params))
            
            # Sign and send transaction
            result = self.client.send_transaction(
                transaction,
                from_keypair
            )
            
            return result['result']
        except Exception as e:
            print(f"Error transferring tokens: {e}")
            return None
    
    def verify_transaction(self, signature: str) -> bool:
        """Verify if a transaction was successful"""
        try:
            result = self.client.confirm_transaction(signature)
            return result['result']
        except Exception as e:
            print(f"Error verifying transaction: {e}")
            return False
