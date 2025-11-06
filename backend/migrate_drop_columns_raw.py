import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def drop_old_purchase_columns():
    """Drop old single-item columns from purchases table using raw SQL"""
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="water_inventory",
            user="postgres",
            password="9876",
            port="5432"
        )
        
        cursor = conn.cursor()
        
        logger.info("Connecting to database...")
        
        # Drop old columns
        old_columns = ['quantity', 'unit_price', 'cost_basis', 'blow_price']
        
        for col in old_columns:
            try:
                sql = f"ALTER TABLE purchases DROP COLUMN IF EXISTS {col} CASCADE;"
                logger.info(f"Executing: {sql}")
                cursor.execute(sql)
                logger.info(f"✅ Dropped column '{col}'")
            except Exception as e:
                logger.warning(f"⚠️  Could not drop column '{col}': {str(e)}")
        
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    drop_old_purchase_columns()
