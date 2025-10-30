import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    # Test basic imports
    from modules.data_loader import LoanDataLoader
    from modules.model_handler import LoanApprovalModel
    print("✅ Basic imports successful!")
    
    # Test data loader
    loader = LoanDataLoader('loan_data.csv')
    df = loader.load_data()
    print(f"✅ Data loaded: {len(df)} rows")
    
    # Test model handler
    model = LoanApprovalModel()
    print("✅ Model handler initialized!")
    
    # Test simple response
    test_response = model.generate_response("Hello, can you help me with loans?")
    print(f"✅ Model response test: {test_response[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()