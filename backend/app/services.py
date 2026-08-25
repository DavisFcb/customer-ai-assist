from typing import Tuple, Dict, Any, List
from app.models import IntentType, AuthenticationStatus, ResponseType
from app.mock_data import (
    CUSTOMERS, get_customer, get_policies_for_customer, 
    get_claims_for_customer, get_payments_for_customer,
    get_claim, get_policy, search_knowledge
)
import json


class IntentDetector:
    """Detect customer intent from their message"""
    
    CLAIM_KEYWORDS = ["claim", "status", "progress", "update", "claim_id", "where"]
    POLICY_KEYWORDS = ["policy", "cover", "active", "product", "plan", "policy_number"]
    PAYMENT_KEYWORDS = ["payment", "premium", "due", "paid", "bill", "invoice", "changed"]
    COMPLAINT_KEYWORDS = ["complaint", "issue", "problem", "concern", "unhappy", "dissatisfied"]
    
    @staticmethod
    def detect(message: str, language: str = "en") -> Tuple[IntentType, float]:
        """
        Detect intent from message.
        Returns (intent, confidence)
        """
        message_lower = message.lower()
        
        # Check for claim status
        if any(kw in message_lower for kw in IntentDetector.CLAIM_KEYWORDS):
            return IntentType.CLAIM_STATUS, 0.96
        
        # Check for policy info
        if any(kw in message_lower for kw in IntentDetector.POLICY_KEYWORDS):
            return IntentType.POLICY_INFO, 0.94
        
        # Check for payment
        if any(kw in message_lower for kw in IntentDetector.PAYMENT_KEYWORDS):
            return IntentType.PAYMENT_STATUS, 0.92
        
        # Check for complaint
        if any(kw in message_lower for kw in IntentDetector.COMPLAINT_KEYWORDS):
            return IntentType.COMPLAINT, 0.90
        
        # Default to general inquiry
        if len(message) > 5:
            return IntentType.GENERAL_INQUIRY, 0.75
        
        return IntentType.UNKNOWN, 0.30


class AuthenticationService:
    """Handle customer authentication"""
    
    @staticmethod
    def verify_customer(customer_id: str) -> Tuple[bool, AuthenticationStatus]:
        """
        Verify customer identity.
        Returns (is_verified, status)
        """
        customer = get_customer(customer_id)
        
        if not customer:
            return False, AuthenticationStatus.FAILED
        
        if customer.get("verified"):
            return True, AuthenticationStatus.VERIFIED
        
        return False, AuthenticationStatus.PENDING
    
    @staticmethod
    def requires_authentication_for_intent(intent: IntentType) -> bool:
        """Check if intent requires authentication"""
        sensitive_intents = [
            IntentType.CLAIM_STATUS,
            IntentType.POLICY_INFO,
            IntentType.PAYMENT_STATUS
        ]
        return intent in sensitive_intents


class LanguageDetector:
    """Detect message language (mock implementation)"""
    
    LANGUAGE_KEYWORDS = {
        "zu": ["iphi", "ungubani", "yini", "noma", "kutheni"],
        "xh": ["uphi", "ubani", "ini", "okanye", "kutheni"],
        "af": ["waar", "wie", "wat", "waarom", "hoe"],
        "en": ["where", "what", "who", "why", "how"]
    }
    
    @staticmethod
    def detect(message: str, provided_language: str = "en") -> Tuple[str, float]:
        """
        Detect message language.
        Returns (language_code, confidence)
        """
        # If provided_language is set, use it with high confidence
        if provided_language and provided_language != "en":
            return provided_language, 0.95
        
        message_lower = message.lower()
        
        # Simple keyword-based detection
        for lang, keywords in LanguageDetector.LANGUAGE_KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                return lang, 0.85
        
        # Default to English
        return "en", 0.99


class AgentRouter:
    """Route intents to appropriate agents"""
    
    INTENT_TO_AGENT = {
        IntentType.CLAIM_STATUS: "claims",
        IntentType.POLICY_INFO: "policies",
        IntentType.PAYMENT_STATUS: "payments",
        IntentType.COMPLAINT: "complaints",
        IntentType.GENERAL_INQUIRY: "general",
        IntentType.UNKNOWN: "escalation"
    }
    
    @staticmethod
    def get_agent(intent: IntentType) -> str:
        """Get agent name for intent"""
        return AgentRouter.INTENT_TO_AGENT.get(intent, "escalation")


class RAGService:
    """Retrieve relevant documents for grounding responses"""
    
    @staticmethod
    def retrieve_documents(intent: IntentType, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge documents"""
        keywords = query.lower().split()
        return search_knowledge(keywords)


class ResponseBuilder:
    """Build responses based on agent results"""
    
    @staticmethod
    def build_verification_response() -> Dict[str, Any]:
        """Build verification request response"""
        return {
            "type": "verification",
            "text": "I need to verify your identity before I can access your policy details. What is your ID number?",
            "data": {
                "method": "id_number"
            }
        }
    
    @staticmethod
    def build_claim_response(claim: Dict[str, Any]) -> Dict[str, Any]:
        """Build claim status response"""
        status_messages = {
            "UNDER_REVIEW": "Your claim is currently under review.",
            "APPROVED": "Your claim has been approved and is being processed for payment.",
            "REJECTED": "Unfortunately, your claim has been rejected.",
            "PENDING_INFO": "We need additional information to process your claim.",
            "PAID": "Your claim has been paid out."
        }
        
        status = claim.get("status", "UNKNOWN")
        text = status_messages.get(status, f"Your claim status is: {status}")
        
        return {
            "type": "claim",
            "text": text,
            "data": {
                "claim_id": claim.get("claim_id"),
                "status": claim.get("status"),
                "last_updated": claim.get("last_updated"),
                "stage": claim.get("stage")
            }
        }
    
    @staticmethod
    def build_policy_response(policy: Dict[str, Any]) -> Dict[str, Any]:
        """Build policy info response"""
        status = policy.get("status", "UNKNOWN")
        text = f"Your {policy.get('product', 'policy')} is currently {status.lower()}."
        
        return {
            "type": "policy",
            "text": text,
            "data": {
                "policy_number": policy.get("policy_number"),
                "product": policy.get("product"),
                "status": policy.get("status"),
                "premium": policy.get("premium")
            }
        }
    
    @staticmethod
    def build_payment_response(payment: Dict[str, Any]) -> Dict[str, Any]:
        """Build payment response"""
        status = payment.get("status", "UNKNOWN")
        text = f"Your latest premium payment of R{payment.get('amount', 0)} was {status.lower()} on {payment.get('date')}."
        
        return {
            "type": "payment",
            "text": text,
            "data": {
                "amount": payment.get("amount"),
                "date": payment.get("date"),
                "status": payment.get("status")
            }
        }
    
    @staticmethod
    def build_handoff_response(reason: str = "LOW_CONFIDENCE", queue: str = "GENERAL") -> Dict[str, Any]:
        """Build human handoff response"""
        return {
            "type": "handoff",
            "text": "I'll connect you with a specialist consultant who can assist you further.",
            "data": {
                "queue": queue,
                "reason": reason
            }
        }
    
    @staticmethod
    def build_text_response(text: str) -> Dict[str, Any]:
        """Build simple text response"""
        return {
            "type": "text",
            "text": text
        }


class ConversationState:
    """Manage conversation state"""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.customer_id: str | None = None
        self.authenticated = False
        self.messages: List[Dict[str, Any]] = []
        self.language = "en"
        self.channel = "web"
    
    def add_message(self, role: str, content: str):
        """Add message to conversation"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": str(__import__("datetime").datetime.now())
        })
    
    def set_customer(self, customer_id: str):
        """Set customer for conversation"""
        self.customer_id = customer_id
    
    def set_authenticated(self, status: bool):
        """Update authentication status"""
        self.authenticated = status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "conversation_id": self.conversation_id,
            "customer_id": self.customer_id,
            "authenticated": self.authenticated,
            "messages": self.messages,
            "language": self.language,
            "channel": self.channel
        }


# Global conversation store (in-memory for mock)
CONVERSATIONS: Dict[str, ConversationState] = {}
