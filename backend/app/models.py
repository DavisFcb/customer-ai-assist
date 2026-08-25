from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


# Enums
class ChannelType(str, Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"
    VOICE = "voice"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    AWAITING_VERIFICATION = "awaiting_verification"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED_VERIFICATION = "failed_verification"
    HANDOFF = "handoff"


class IntentType(str, Enum):
    CLAIM_STATUS = "CLAIM_STATUS"
    POLICY_INFO = "POLICY_INFO"
    PAYMENT_STATUS = "PAYMENT_STATUS"
    COMPLAINT = "COMPLAINT"
    GENERAL_INQUIRY = "GENERAL_INQUIRY"
    UNKNOWN = "UNKNOWN"


class AuthenticationStatus(str, Enum):
    REQUIRED = "required"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class ResponseType(str, Enum):
    TEXT = "text"
    CLAIM = "claim"
    POLICY = "policy"
    PAYMENT = "payment"
    VERIFICATION = "verification"
    HANDOFF = "handoff"


class NextActionType(str, Enum):
    NONE = "none"
    VERIFICATION = "verification"
    ESCALATION = "escalation"
    CALLBACK = "callback"


# Request Models
class CreateConversationRequest(BaseModel):
    channel: ChannelType
    language: str = "en"


class CustomerInfo(BaseModel):
    id_number: str


class MessageData(BaseModel):
    text: str


class SendMessageRequest(BaseModel):
    message: MessageData
    customer: CustomerInfo
    language: str = "en"
    channel: ChannelType


# Response Models
class LanguageResponse(BaseModel):
    code: str
    confidence: float


class IntentResponse(BaseModel):
    name: IntentType
    confidence: float


class AuthenticationResponse(BaseModel):
    required: bool
    status: AuthenticationStatus


class AgentResponse(BaseModel):
    name: str
    status: str


class TextResponseData(BaseModel):
    type: Literal["text"]
    text: str


class ClaimData(BaseModel):
    claim_id: str
    status: str
    last_updated: str


class ClaimResponseData(BaseModel):
    type: Literal["claim"]
    text: str
    data: ClaimData


class PolicyData(BaseModel):
    policy_number: str
    product: str
    status: str


class PolicyResponseData(BaseModel):
    type: Literal["policy"]
    text: str
    data: PolicyData


class PaymentData(BaseModel):
    amount: float
    date: str
    status: str


class PaymentResponseData(BaseModel):
    type: Literal["payment"]
    text: str
    data: PaymentData


class VerificationData(BaseModel):
    method: str


class VerificationResponseData(BaseModel):
    type: Literal["verification"]
    text: str
    data: VerificationData


class HandoffData(BaseModel):
    queue: str
    reason: str


class HandoffResponseData(BaseModel):
    type: Literal["handoff"]
    text: str
    data: HandoffData


class NextAction(BaseModel):
    type: NextActionType
    reason: Optional[str] = None


class SendMessageResponse(BaseModel):
    conversation_id: str
    status: ConversationStatus
    language: LanguageResponse
    intent: IntentResponse
    authentication: AuthenticationResponse
    agent: AgentResponse
    response: Dict[str, Any]  # Flexible for all response types
    sources: List[str] = []
    next_action: NextAction


class CreateConversationResponse(BaseModel):
    conversation_id: str
    status: ConversationStatus


class GetConversationResponse(BaseModel):
    conversation_id: str
    status: ConversationStatus
    channel: ChannelType
    language: str
    customer_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    created_at: str
    updated_at: str
