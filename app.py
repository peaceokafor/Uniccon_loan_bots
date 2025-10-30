import streamlit as st
import pandas as pd
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.data_loader import LoanDataLoader
from modules.chat_engine import LoanApprovalChatEngine
from modules.utils import *

# Page configuration
st.set_page_config(
    page_title="Uniccon Loan Approval Bot",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
# Initialize session state
if 'chat_engine' not in st.session_state:
    try:
        st.session_state.chat_engine = LoanApprovalChatEngine('loan_data.csv')
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Note: AI features limited - {e}")
        # Create a basic chat engine that will use fallbacks
        st.session_state.chat_engine = None
        st.session_state.messages = []

if 'data_loaded' not in st.session_state:
    try:
        st.session_state.data_loader = LoanDataLoader('loan_data.csv')
        st.session_state.df = st.session_state.data_loader.load_data()
        st.session_state.stats = st.session_state.data_loader.get_approval_stats()
        st.session_state.data_loaded = True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.session_state.data_loaded = False

def main():
    # Header
    st.title("🏦 Uniccon Loan Approval Bot")
    st.markdown("""
    Welcome to the AI-powered loan approval assistant! I can help you analyze loan applications, 
    provide insights from historical data, and guide you through the loan approval process.
    """)
    
    # Sidebar
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose a section",
        ["Chat with Bot", "Data Analysis", "Loan Application Analysis", "About"]
    )
    
    if app_mode == "Chat with Bot":
        display_chat_interface()
    elif app_mode == "Data Analysis":
        display_data_analysis()
    elif app_mode == "Loan Application Analysis":
        display_loan_analysis()
    else:
        display_about()

def display_chat_interface():
    st.header("💬 Chat with Uniccon Loan Bot")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about loan approvals, criteria, or financial advice..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    if st.session_state.chat_engine:
                        response = st.session_state.chat_engine.process_message(prompt)
                    else:
                        # Fallback response if chat engine failed to initialize
                        response = "I can provide general loan guidance. For AI features, please ensure Ollama is installed and running."
            
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I'm here to help with loan information! For full AI features, please check that Ollama is installed. Error: {str(e)}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_engine.clear_history()
        st.rerun()

def display_data_analysis():
    st.header("📊 Loan Data Analysis")
    
    if not st.session_state.data_loaded:
        st.error("Data not loaded. Please check if loan_data.csv exists.")
        return
    
    # Display statistics
    st.subheader("Key Statistics")
    display_loan_stats(st.session_state.stats)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        create_approval_chart(st.session_state.df)
    
    with col2:
        create_income_vs_credit_chart(st.session_state.df)
    
    # Sample data
    st.subheader("Sample Loan Applications")
    st.dataframe(st.session_state.data_loader.get_sample_data(10), use_container_width=True)

def display_loan_analysis():
    st.header("📝 Loan Application Analysis")
    
    st.markdown("""
    Enter your loan application details below to get an AI-powered analysis of your approval chances
    and personalized recommendations.
    """)
    
    with st.form("loan_application"):
        col1, col2 = st.columns(2)
        
        with col1:
            income = st.number_input("Annual Income ($)", min_value=0, value=50000, step=1000)
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=700)
            employment_status = st.selectbox("Employment Status", ["employed", "unemployed"])
        
        with col2:
            loan_amount = st.number_input("Loan Amount ($)", min_value=0, value=25000, step=1000)
            dti_ratio = st.number_input("DTI Ratio (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
            loan_purpose = st.text_input("Loan Purpose", "Personal loan")
        
        submitted = st.form_submit_button("Analyze Application")
        
        if submitted:
            # Validate inputs
            errors = validate_loan_inputs(income, credit_score, loan_amount, dti_ratio)
            
            if errors:
                for field, error in errors.items():
                    st.error(f"{field.replace('_', ' ').title()}: {error}")
            else:
                with st.spinner("Analyzing your application..."):
                    try:
                        application_data = {
                            'income': income,
                            'credit_score': credit_score,
                            'loan_amount': loan_amount,
                            'dti_ratio': dti_ratio,
                            'employment_status': employment_status,
                            'purpose': loan_purpose
                        }
                        
                        analysis_result = st.session_state.chat_engine.get_approval_analysis(application_data)
                        
                        # Display results
                        st.subheader("Analysis Results")
                        
                        # Score gauge
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = analysis_result['score'],
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Approval Score"},
                            gauge = {
                                'axis': {'range': [None, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 40], 'color': "red"},
                                    {'range': [40, 60], 'color': "yellow"},
                                    {'range': [60, 80], 'color': "lightgreen"},
                                    {'range': [80, 100], 'color': "green"}
                                ]
                            }
                        ))
                        st.plotly_chart(fig)
                        
                        # Factors and recommendations
                        st.subheader("Key Factors")
                        for factor in analysis_result['factors']:
                            st.write(f"• {factor}")
                        
                        st.subheader("AI Analysis")
                        st.write(analysis_result['analysis'])
                        
                        st.subheader("Overall Recommendation")
                        st.info(analysis_result['recommendation'])
                        
                    except Exception as e:
                        st.error(f"Error analyzing application: {str(e)}")

def display_about():
    st.header("ℹ️ About Uniccon Loan Approval Bot")
    
    st.markdown("""
    ## 🏦 Uniccon Loan Approval Bot
    
    This AI-powered chatbot helps analyze loan applications and provide insights based on historical loan data.
    
    ### Features:
    
    - **💬 Intelligent Chat**: Ask questions about loan criteria, approval processes, and financial advice
    - **📊 Data Analysis**: Explore historical loan approval patterns and statistics
    - **📝 Application Analysis**: Get AI-powered analysis of your loan application
    - **🤖 AI-Powered Insights**: Leverages machine learning for personalized recommendations
    
    ### Technology Stack:
    
    - **Streamlit**: Web application framework
    - **LangChain**: LLM application framework
    - **Ollama**: Local LLM deployment
    - **Plotly**: Interactive visualizations
    - **Pandas**: Data analysis and manipulation
    
    ### How to Use:
    
    1. **Chat**: Ask natural language questions about loans
    2. **Data Analysis**: Explore historical approval patterns
    3. **Application Analysis**: Submit your details for personalized analysis
    
    ### Data Source:
    
    The analysis is based on a comprehensive loan approval dataset containing:
    - Income levels
    - Credit scores
    - Loan amounts
    - Debt-to-Income ratios
    - Employment status
    - Approval outcomes
    """)

if __name__ == "__main__":
    main()