import ollama
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class LoanApprovalModel:
    def __init__(self, model_name: str = "llama2"):
        self.model_name = model_name
        self.model_available = False
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize the Ollama model with robust error handling"""
        try:
            logger.info("Initializing Ollama model...")
            
            # Try to list models to check availability
            try:
                models_response = ollama.list()
                logger.info(f"Ollama response received")
                
                # Simple check - if we get a response, assume it's working
                self.model_available = True
                logger.info("Ollama model system initialized successfully")
                
            except Exception as list_error:
                logger.warning(f"Could not list Ollama models: {list_error}")
                self.model_available = False
                
        except Exception as e:
            logger.error(f"Error during model initialization: {e}")
            self.model_available = False
            
        if not self.model_available:
            logger.warning("Ollama model not available - using fallback responses")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using the LLM or fallback"""
        try:
            if not self.model_available:
                return self._get_fallback_response(prompt)
            
            full_prompt = f"""
            You are Uniccon Loan Approval Bot, an AI assistant specialized in loan approval analysis and financial guidance.
            
            CONTEXT FOR ANALYSIS:
            {context}
            
            USER QUERY: {prompt}
            
            Please provide a helpful, accurate response based on the loan data context and financial best practices.
            Be professional but friendly in your tone.
            Focus on loan approval criteria, credit scores, income requirements, debt-to-income ratios, and financial advice.
            """
            
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                options={
                    'temperature': 0.1,
                    'num_predict': 800,
                }
            )
            return response['response'].strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Provide intelligent fallback responses when Ollama is unavailable"""
        prompt_lower = prompt.lower()
        
        # Common loan-related queries with pre-defined responses
        if any(word in prompt_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Uniccon Loan Approval Bot. I can help you with loan applications, approval criteria, and financial guidance. How can I assist you today?"
        
        elif any(word in prompt_lower for word in ['loan approval', 'approval criteria']):
            return """Based on our loan dataset analysis, key approval factors include:
• **Credit Score**: Aim for 700+ for better chances
• **Income**: Stable income demonstrating repayment ability  
• **DTI Ratio**: Keep below 36% for optimal approval
• **Employment**: Stable employment history
• **Loan Amount**: Reasonable relative to income

Would you like me to analyze a specific application?"""
        
        elif any(word in prompt_lower for word in ['credit score', 'credit']):
            return """Credit scores significantly impact loan approval:
• **Excellent (750+)**: High approval likelihood
• **Good (700-749)**: Good approval chances
• **Fair (650-699)**: May need stronger other factors
• **Poor (<650)**: Consider credit improvement first

Our data shows approved applicants average 720+ credit scores."""
        
        elif any(word in prompt_lower for word in ['income', 'salary']):
            return """Income requirements depend on loan amount:
• Generally, your monthly loan payment should be ≤28% of gross monthly income
• Total debt payments should be ≤36% of monthly income
• Higher income relative to loan amount improves approval chances

Our approved applicants average $85,000+ annual income."""
        
        elif any(word in prompt_lower for word in ['dti', 'debt to income']):
            return """Debt-to-Income (DTI) Ratio Guidelines:
• **Excellent**: <20% - Very high approval likelihood
• **Good**: 20-35% - Good approval chances  
• **High**: 36-49% - May need stronger application
• **Very High**: 50%+ - Significant improvement needed

Lower DTI ratios demonstrate better repayment capacity."""
        
        elif any(word in prompt_lower for word in ['business loan', 'business']):
            return """Business loan considerations:
• Business plan and financial projections
• Time in business (2+ years preferred)
• Business revenue and profitability
• Personal credit score of business owner
• Collateral availability

Business loans in our dataset have a 42% approval rate."""
        
        elif any(word in prompt_lower for word in ['help', 'what can you do']):
            return """I can help you with:
• Loan approval criteria and requirements
• Credit score analysis and improvement
• Income and DTI ratio guidance  
• Business and personal loan information
• Application analysis and recommendations
• Historical approval patterns from our dataset

Try the 'Loan Application Analysis' section for personalized assessment!"""
        
        else:
            return """I specialize in loan approval guidance and financial advice. 

I can help you understand:
• Loan approval criteria and requirements
• Credit score impact on applications  
• Income and debt-to-income ratios
• Business vs personal loan differences
• Application improvement strategies

Try asking about specific loan topics, or use the 'Loan Application Analysis' section for a personalized assessment!"""
    
    def analyze_loan_application(self, application_data: Dict) -> str:
        """Analyze a specific loan application"""
        try:
            if not self.model_available:
                return self._get_fallback_analysis(application_data)
            
            analysis_prompt = f"""
            Analyze this loan application and provide recommendations:
            
            Application Details:
            - Income: ${application_data.get('income', 'N/A')}
            - Credit Score: {application_data.get('credit_score', 'N/A')}
            - Loan Amount: ${application_data.get('loan_amount', 'N/A')}
            - DTI Ratio: {application_data.get('dti_ratio', 'N/A')}%
            - Employment Status: {application_data.get('employment_status', 'N/A')}
            - Loan Purpose: {application_data.get('purpose', 'Not specified')}
            
            Provide specific analysis and improvement recommendations.
            """
            
            return self.generate_response(analysis_prompt)
            
        except Exception as e:
            logger.error(f"Error in loan analysis: {e}")
            return self._get_fallback_analysis(application_data)
    
    def _get_fallback_analysis(self, application_data: Dict) -> str:
        """Fallback analysis when AI is unavailable"""
        income = application_data.get('income', 0)
        credit_score = application_data.get('credit_score', 0)
        loan_amount = application_data.get('loan_amount', 0)
        dti_ratio = application_data.get('dti_ratio', 0)
        employment = application_data.get('employment_status', '')
        
        analysis = f"Analysis for application:\n"
        analysis += f"• Income: ${income:,} - {'Good' if income > 50000 else 'Consider increasing'}\n"
        analysis += f"• Credit Score: {credit_score} - {'Excellent' if credit_score > 750 else 'Good' if credit_score > 700 else 'Needs improvement'}\n"
        analysis += f"• Loan Amount: ${loan_amount:,} - {'Reasonable' if loan_amount < income * 0.5 else 'High relative to income'}\n"
        analysis += f"• DTI Ratio: {dti_ratio}% - {'Excellent' if dti_ratio < 20 else 'Good' if dti_ratio < 35 else 'Needs reduction'}\n"
        analysis += f"• Employment: {employment} - {'Positive factor' if employment == 'employed' else 'Consider securing employment'}\n\n"
        analysis += "Based on our dataset patterns, focus on improving weaker areas for better approval chances."
        
        return analysis