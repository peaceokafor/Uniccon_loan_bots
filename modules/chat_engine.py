import logging
from typing import List, Dict, Any
from modules.model_handler import LoanApprovalModel
from modules.data_loader import LoanDataLoader

logger = logging.getLogger(__name__)

class ChatMessage:
    """Simple message class to replace LangChain messages"""
    def __init__(self, content: str, role: str):
        self.content = content
        self.role = role

class LoanApprovalChatEngine:
    def __init__(self, data_file_path: str, model_name: str = "llama2"):
        self.data_loader = LoanDataLoader(data_file_path)
        self.conversation_history: List[ChatMessage] = []
        self.data_context = ""
        
        # Initialize model with error handling
        try:
            self.model_handler = LoanApprovalModel(model_name)
        except Exception as e:
            logger.error(f"Error initializing model handler: {e}")
            # Model handler will use fallbacks automatically
        
        self.initialize_data_context()
        
    def initialize_data_context(self):
        """Initialize the data context for the chatbot"""
        try:
            self.data_loader.load_data()
            stats = self.data_loader.get_approval_stats()
            
            self.data_context = f"""
            LOAN APPROVAL DATASET INSIGHTS:
            - Total Applications: {stats['total_applications']}
            - Approved: {stats['approved']} ({stats['approval_rate']:.1f}%)
            - Rejected: {stats['rejected']}
            - Average Income (Approved): ${stats['avg_income_approved']:,.2f}
            - Average Income (Rejected): ${stats['avg_income_rejected']:,.2f}
            - Average Credit Score (Approved): {stats['avg_credit_score_approved']:.1f}
            - Average Credit Score (Rejected): {stats['avg_credit_score_rejected']:.1f}
            
            KEY PATTERNS:
            1. Higher income and credit scores correlate with approval
            2. Lower DTI ratios improve approval chances
            3. Employment status significantly impacts decisions
            4. Business and education loans have varying approval rates
            """
            
        except Exception as e:
            logger.error(f"Error initializing data context: {e}")
            self.data_context = "Data context unavailable due to loading error."
    
    def process_message(self, user_message: str) -> str:
        """Process user message and generate response"""
        try:
            # Add user message to history
            self.conversation_history.append(ChatMessage(content=user_message, role="user"))
            
            # Generate response
            bot_response = self.model_handler.generate_response(
                prompt=user_message,
                context=self.data_context
            )
            
            # Add bot response to history
            self.conversation_history.append(ChatMessage(content=bot_response, role="assistant"))
            
            # Limit conversation history to prevent memory issues
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
                
            return bot_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "I apologize, but I encountered an error processing your message. Please try again."
    
    def get_approval_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed approval analysis for user data"""
        try:
            analysis = self.model_handler.analyze_loan_application(user_data)
            
            # Basic scoring based on common criteria
            score = 0
            factors = []
            
            # Income scoring
            income = user_data.get('income', 0)
            if income > 75000:
                score += 25
                factors.append("Good income level")
            elif income > 50000:
                score += 15
                factors.append("Moderate income level")
            else:
                factors.append("Low income level - consider increasing income")
            
            # Credit score scoring
            credit_score = user_data.get('credit_score', 0)
            if credit_score > 750:
                score += 30
                factors.append("Excellent credit score")
            elif credit_score > 700:
                score += 20
                factors.append("Good credit score")
            elif credit_score > 650:
                score += 10
                factors.append("Fair credit score - consider improvement")
            else:
                factors.append("Poor credit score - significant improvement needed")
            
            # DTI ratio scoring
            dti_ratio = user_data.get('dti_ratio', 0)
            if dti_ratio < 20:
                score += 25
                factors.append("Excellent DTI ratio")
            elif dti_ratio < 35:
                score += 15
                factors.append("Good DTI ratio")
            elif dti_ratio < 50:
                score += 5
                factors.append("High DTI ratio - consider reduction")
            else:
                factors.append("Very high DTI ratio - significant reduction needed")
            
            # Employment status
            employment_status = user_data.get('employment_status', '')
            if employment_status.lower() == 'employed':
                score += 20
                factors.append("Employed - positive factor")
            else:
                factors.append("Unemployed - consider securing employment")
            
            return {
                'analysis': analysis,
                'score': min(score, 100),
                'factors': factors,
                'recommendation': self._get_recommendation(score)
            }
            
        except Exception as e:
            logger.error(f"Error in approval analysis: {e}")
            return {
                'analysis': "Unable to perform analysis due to error.",
                'score': 0,
                'factors': [],
                'recommendation': 'Please check your input data.'
            }
    
    def _get_recommendation(self, score: int) -> str:
        """Get recommendation based on score"""
        if score >= 80:
            return "Strong candidate for loan approval"
        elif score >= 60:
            return "Good candidate, minor improvements possible"
        elif score >= 40:
            return "Moderate candidate, significant improvements needed"
        else:
            return "Weak candidate, major improvements required"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []