from solana.rpc.api import Client
from solana.transaction import Transaction, TransactionInstruction, AccountMeta
from solana.system_program import CreateAccountParams, create_account
from solana.keypair import Keypair
from typing import List, Dict, Any
import json
import base58

class SmartContract:
    def __init__(self, program_id: str, solana_client: Client):
        self.program_id = program_id
        self.client = solana_client
        
    def create_data_sharing_agreement(
        self,
        owner_keypair: Keypair,
        user_pubkey: str,
        dataset_id: str,
        access_duration: int,
        price: float
    ) -> str:
        """Create a data sharing agreement on the blockchain"""
        try:
            # Create agreement account
            agreement_keypair = Keypair()
            
            # Calculate required space for the agreement data
            space = 1000  # Adjust based on actual data size needs
            
            # Calculate minimum balance for rent exemption
            resp = self.client.get_minimum_balance_for_rent_exemption(space)
            lamports = resp['result']
            
            # Create account transaction
            create_account_params = CreateAccountParams(
                from_pubkey=owner_keypair.public_key,
                new_account_pubkey=agreement_keypair.public_key,
                lamports=lamports,
                space=space,
                program_id=self.program_id
            )
            
            # Create the agreement data
            agreement_data = {
                'owner': str(owner_keypair.public_key),
                'user': user_pubkey,
                'dataset_id': dataset_id,
                'access_duration': access_duration,
                'price': price,
                'status': 'pending'
            }
            
            # Serialize the agreement data
            serialized_data = json.dumps(agreement_data).encode()
            
            # Create instruction to initialize the agreement
            instruction = TransactionInstruction(
                keys=[
                    AccountMeta(pubkey=agreement_keypair.public_key, is_signer=True, is_writable=True),
                    AccountMeta(pubkey=owner_keypair.public_key, is_signer=True, is_writable=False)
                ],
                program_id=self.program_id,
                data=serialized_data
            )
            
            # Create and send transaction
            transaction = Transaction().add(
                create_account(create_account_params)
            ).add(instruction)
            
            # Sign and send transaction
            result = self.client.send_transaction(
                transaction,
                owner_keypair,
                agreement_keypair
            )
            
            return result['result']
            
        except Exception as e:
            raise Exception(f"Error creating agreement: {str(e)}")
    
    def execute_agreement(
        self,
        agreement_pubkey: str,
        user_keypair: Keypair,
        payment_amount: float
    ) -> str:
        """Execute a data sharing agreement"""
        try:
            # Convert SOL to lamports
            lamports = int(payment_amount * 10**9)
            
            # Create instruction for agreement execution
            instruction = TransactionInstruction(
                keys=[
                    AccountMeta(pubkey=agreement_pubkey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=user_keypair.public_key, is_signer=True, is_writable=True)
                ],
                program_id=self.program_id,
                data=b'execute'
            )
            
            # Create and send transaction
            transaction = Transaction().add(instruction)
            
            result = self.client.send_transaction(
                transaction,
                user_keypair
            )
            
            return result['result']
            
        except Exception as e:
            raise Exception(f"Error executing agreement: {str(e)}")
    
    def verify_agreement(self, agreement_pubkey: str) -> Dict[str, Any]:
        """Verify the status of a data sharing agreement"""
        try:
            # Get account info
            result = self.client.get_account_info(agreement_pubkey)
            
            if not result['result']['value']:
                raise Exception("Agreement not found")
            
            # Decode and parse the agreement data
            data = base58.b58decode(result['result']['value']['data'][0])
            agreement_data = json.loads(data.decode())
            
            return agreement_data
            
        except Exception as e:
            raise Exception(f"Error verifying agreement: {str(e)}")
    
    def revoke_agreement(
        self,
        agreement_pubkey: str,
        owner_keypair: Keypair
    ) -> str:
        """Revoke a data sharing agreement"""
        try:
            # Create instruction for agreement revocation
            instruction = TransactionInstruction(
                keys=[
                    AccountMeta(pubkey=agreement_pubkey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=owner_keypair.public_key, is_signer=True, is_writable=False)
                ],
                program_id=self.program_id,
                data=b'revoke'
            )
            
            # Create and send transaction
            transaction = Transaction().add(instruction)
            
            result = self.client.send_transaction(
                transaction,
                owner_keypair
            )
            
            return result['result']
            
        except Exception as e:
            raise Exception(f"Error revoking agreement: {str(e)}")
