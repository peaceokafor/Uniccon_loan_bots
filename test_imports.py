import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.data_loader import LoanDataLoader
    from modules.model_handler import LoanApprovalModel
    from modules.chat_engine import LoanApprovalChatEngine
    print("✅ All modules imported successfully!")
    
    # Test data loader
    loader = LoanDataLoader('loan_data.csv')
    df = loader.load_data()
    print(f"✅ Data loaded: {len(df)} rows")
    
except Exception as e:
    print(f"❌ Error: {e}")