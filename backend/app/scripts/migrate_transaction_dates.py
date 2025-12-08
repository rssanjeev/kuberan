"""
Migrate existing transactions to add transaction_year and transaction_month fields.

This script backfills the new transaction_year and transaction_month fields
for existing transactions using the same logic as the repository:
- If transaction month > statement month, it's from previous year
- Otherwise, use statement year
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def migrate_transactions():
    """Migrate existing transactions to add transaction_year and transaction_month."""
    
    # Get MongoDB connection from environment
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://mongodb:27017')
    database_name = os.getenv('DATABASE_NAME', 'kuberan')
    
    print(f"Connecting to MongoDB: {mongodb_url}/{database_name}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client[database_name]
    transactions_collection = db['credit_card_transactions']
    
    print("Starting transaction date migration")
    
    # Find all transactions without transaction_year field
    query = {"transaction_year": {"$exists": False}}
    transactions = await transactions_collection.find(query).to_list(None)
    
    total = len(transactions)
    print(f"Found {total} transactions to migrate")
    
    if total == 0:
        print("No transactions to migrate")
        return
    
    updated = 0
    errors = 0
    
    for txn in transactions:
        try:
            # Parse transaction date: "MM/DD"
            transaction_date = txn.get('transaction_date', '')
            statement_year = txn.get('statement_year')
            statement_month = txn.get('statement_month')
            
            if not transaction_date or not statement_year or not statement_month:
                print(f"Skipping transaction {txn.get('_id')} - missing data")
                errors += 1
                continue
            
            # Parse MM/DD format
            date_parts = transaction_date.split('/')
            if len(date_parts) == 2:
                txn_month = int(date_parts[0])
                
                # Infer transaction year using billing cycle logic
                # If transaction month > statement month, it's from previous year
                if txn_month > statement_month:
                    txn_year = statement_year - 1
                else:
                    txn_year = statement_year
            else:
                # Fallback: use statement month/year
                txn_month = statement_month
                txn_year = statement_year
                print(f"Invalid date format for {txn.get('_id')}, using fallback")
            
            # Update transaction
            result = await transactions_collection.update_one(
                {"_id": txn['_id']},
                {
                    "$set": {
                        "transaction_year": txn_year,
                        "transaction_month": txn_month
                    }
                }
            )
            
            if result.modified_count > 0:
                updated += 1
                if updated % 100 == 0:
                    print(f"Migrated {updated}/{total} transactions")
            
        except Exception as e:
            print(f"Error migrating transaction {txn.get('_id')}: {str(e)}")
            errors += 1
    
    print(f"Migration completed: {updated} updated, {errors} errors out of {total} total")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate_transactions())
