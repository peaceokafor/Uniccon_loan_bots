import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
import logging

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def display_loan_stats(stats: Dict[str, Any]):
    """Display loan statistics in Streamlit"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", stats['total_applications'])
    
    with col2:
        st.metric("Approved", stats['approved'])
    
    with col3:
        st.metric("Rejected", stats['rejected'])
    
    with col4:
        st.metric("Approval Rate", f"{stats['approval_rate']:.1f}%")

def create_approval_chart(df: pd.DataFrame):
    """Create approval rate visualization"""
    fig = px.pie(
        names=['Approved', 'Rejected'],
        values=[len(df[df['Approval'] == 'Approved']), len(df[df['Approval'] == 'Rejected'])],
        title='Loan Approval Distribution'
    )
    st.plotly_chart(fig)

def create_income_vs_credit_chart(df: pd.DataFrame):
    """Create income vs credit score scatter plot"""
    fig = px.scatter(
        df, 
        x='Income', 
        y='Credit_Score', 
        color='Approval',
        title='Income vs Credit Score by Approval Status',
        hover_data=['Loan_Amount', 'DTI_Ratio']
    )
    st.plotly_chart(fig)

def validate_loan_inputs(income: float, credit_score: int, loan_amount: float, dti_ratio: float) -> Dict[str, str]:
    """Validate loan application inputs"""
    errors = {}
    
    if income <= 0:
        errors['income'] = "Income must be positive"
    
    if credit_score < 300 or credit_score > 850:
        errors['credit_score'] = "Credit score must be between 300 and 850"
    
    if loan_amount <= 0:
        errors['loan_amount'] = "Loan amount must be positive"
    
    if dti_ratio < 0 or dti_ratio > 100:
        errors['dti_ratio'] = "DTI ratio must be between 0 and 100"
    
    return errors