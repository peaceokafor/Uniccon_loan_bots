import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class LoanDataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.features = None
        self.target = None
        
    def load_data(self) -> pd.DataFrame:
        """Load and preprocess the loan data"""
        try:
            self.df = pd.read_csv(self.file_path)
            logger.info(f"Data loaded successfully. Shape: {self.df.shape}")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
            
    def preprocess_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Preprocess the data for analysis"""
        if self.df is None:
            self.load_data()
            
        # Create a copy for preprocessing
        df_processed = self.df.copy()
        
        # Convert Approval to binary
        df_processed['Approval_Binary'] = df_processed['Approval'].map({'Approved': 1, 'Rejected': 0})
        
        # Handle employment status
        df_processed['Employment_Status_Binary'] = df_processed['Employment_Status'].map({'employed': 1, 'unemployed': 0})
        
        # Basic feature engineering
        df_processed['Loan_to_Income_Ratio'] = df_processed['Loan_Amount'] / (df_processed['Income'] + 1)
        df_processed['Credit_Score_Group'] = pd.cut(df_processed['Credit_Score'], 
                                                 bins=[0, 580, 670, 740, 800, 850], 
                                                 labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])
        
        self.features = df_processed[['Income', 'Credit_Score', 'Loan_Amount', 'DTI_Ratio', 
                                    'Employment_Status_Binary', 'Loan_to_Income_Ratio']]
        self.target = df_processed['Approval_Binary']
        
        return df_processed, self.target
    
    def get_approval_stats(self) -> Dict:
        """Get approval statistics"""
        if self.df is None:
            self.load_data()
            
        stats = {
            'total_applications': len(self.df),
            'approved': len(self.df[self.df['Approval'] == 'Approved']),
            'rejected': len(self.df[self.df['Approval'] == 'Rejected']),
            'approval_rate': len(self.df[self.df['Approval'] == 'Approved']) / len(self.df) * 100,
            'avg_income_approved': self.df[self.df['Approval'] == 'Approved']['Income'].mean(),
            'avg_income_rejected': self.df[self.df['Approval'] == 'Rejected']['Income'].mean(),
            'avg_credit_score_approved': self.df[self.df['Approval'] == 'Approved']['Credit_Score'].mean(),
            'avg_credit_score_rejected': self.df[self.df['Approval'] == 'Rejected']['Credit_Score'].mean()
        }
        
        return stats
    
    def get_sample_data(self, n: int = 5) -> pd.DataFrame:
        """Get sample data for display"""
        if self.df is None:
            self.load_data()
        return self.df.head(n)