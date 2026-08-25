import os
import uuid
import logging
from datetime import datetime
from xml.sax.saxutils import escape

import httpx
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.models import (
    CreateConversationRequest, CreateConversationResponse,
    SendMessageRequest, SendMessageResponse,
    GetConversationResponse,
    ConversationStatus, AuthenticationStatus, NextActionType
)
from app.services import (
    IntentDetector, AuthenticationService, LanguageDetector,
    AgentRouter, ResponseBuilder, ConversationState,
    CONVERSATIONS
)
from app.mock_data import (
    get_customer, get_customer_by_phone, get_claims_for_customer, get_policies_for_customer,
    get_payments_for_customer, get_claim, get_policy
)

logger = logging.getLogger("uvicorn.error")

# RAG model endpoint that answers customer questions
RAG_API_URL = os.getenv(
    "RAG_API_URL",
    "https://gmjwl5jsbj.execute-api.us-east-1.amazonaws.com/liberty-ai-whatsapp-webhook"
)
# Used when the inbound WhatsApp number isn't linked to a known customer (e.g. sandbox testing)
DEFAULT_RSA_ID = os.getenv("DEFAULT_RSA_ID", "5612095944082")

app = FastAPI(
    title="LibertyAI Assist API",
    description="Mock FastAPI backend for LibertyAI Assist - AI-powered insurance customer service platform",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(""),
):
    """
    Twilio WhatsApp webhook. Forwards the inbound message to the RAG model and
    replies with TwiML so Twilio sends the answer back over WhatsApp.
    """
    phone = From.replace("whatsapp:", "").strip()
    text = Body.strip()

    customer = get_customer_by_phone(phone)
    rsa_id = customer["id"] if customer else DEFAULT_RSA_ID

    reply_text = "Sorry, I couldn't process your request right now. Please try again shortly."

    if text:
        payload = {
            "channel": "whatsapp",
            "session_id": phone,
            "rsa_id": rsa_id,
            "text": text
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(RAG_API_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
                reply_text = (
                    data.get("response")
                    or data.get("text")
                    or data.get("answer")
                    or data.get("message")
                    or reply_text
                )
        except Exception:
            logger.exception("Failed to get response from RAG model for %s", phone)

    twiml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{escape(reply_text)}</Message></Response>"
    )
    return Response(content=twiml, media_type="application/xml")


@app.post("/api/v1/conversations", response_model=CreateConversationResponse)
def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation.
    
    - **channel**: web, whatsapp, or voice
    - **language**: ISO language code (en, zu, xh, af)
    """
    conversation_id = f"conv_{uuid.uuid4().hex[:6].upper()}"
    
    state = ConversationState(conversation_id)
    state.channel = request.channel
    state.language = request.language
    
    CONVERSATIONS[conversation_id] = state
    
    return CreateConversationResponse(
        conversation_id=conversation_id,
        status=ConversationStatus.ACTIVE
    )


@app.get("/api/v1/conversations/{conversation_id}", response_model=GetConversationResponse)
def get_conversation(conversation_id: str):
    """
    Retrieve conversation state and message history.
    """
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    state = CONVERSATIONS[conversation_id]
    
    return GetConversationResponse(
        conversation_id=conversation_id,
        status=ConversationStatus.ACTIVE,
        channel=state.channel,
        language=state.language,
        customer_id=state.customer_id,
        messages=state.messages,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )


@app.post("/api/v1/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a customer message and receive an AI response.
    
    This endpoint handles:
    - Intent detection (claim, policy, payment, complaint, general)
    - Language detection
    - Customer authentication
    - Agent routing and response generation
    - RAG-based knowledge retrieval
    - Human escalation when needed
    """
    # Validate conversation exists
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    state = CONVERSATIONS[conversation_id]
    customer_id = request.customer.id_number
    
    # Set customer on first message
    if not state.customer_id:
        state.customer_id = customer_id
    
    # Verify customer exists
    customer = get_customer(customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    message_text = request.message.text
    state.add_message("user", message_text)
    
    # Detect language
    language_code, language_confidence = LanguageDetector.detect(
        message_text, 
        request.language
    )
    
    # Detect intent
    intent, intent_confidence = IntentDetector.detect(message_text, language_code)
    
    # Check authentication requirement
    auth_required = AuthenticationService.requires_authentication_for_intent(intent)
    is_authenticated, auth_status = AuthenticationService.verify_customer(customer_id)
    
    # Build response
    conversation_status = ConversationStatus.ACTIVE
    agent_name = AgentRouter.get_agent(intent)
    agent_status = "completed"
    response_data = None
    next_action = NextActionType.NONE
    
    # If authentication required but not verified
    if auth_required and not is_authenticated:
        conversation_status = ConversationStatus.AWAITING_VERIFICATION
        agent_status = "pending"
        response_data = ResponseBuilder.build_verification_response()
        auth_status = AuthenticationStatus.REQUIRED
        next_action = NextActionType.VERIFICATION
    else:
        # Customer is authenticated or intent doesn't require auth
        if auth_required:
            auth_status = AuthenticationStatus.VERIFIED
            state.set_authenticated(True)
        else:
            auth_status = AuthenticationStatus.REQUIRED
        
        # Route to appropriate agent
        if intent.value == "CLAIM_STATUS":
            # Get customer's claims
            claims = get_claims_for_customer(customer_id)
            if claims:
                # Return most recent claim
                latest_claim = max(claims, key=lambda x: x["last_updated"])
                response_data = ResponseBuilder.build_claim_response(latest_claim)
            else:
                response_data = ResponseBuilder.build_text_response(
                    "You don't have any claims on record."
                )
        
        elif intent.value == "POLICY_INFO":
            # Get customer's policies
            policies = get_policies_for_customer(customer_id)
            if policies:
                # Return first active policy
                active = [p for p in policies if p["status"] == "ACTIVE"]
                policy = active[0] if active else policies[0]
                response_data = ResponseBuilder.build_policy_response(policy)
            else:
                response_data = ResponseBuilder.build_text_response(
                    "You don't have any active policies."
                )
        
        elif intent.value == "PAYMENT_STATUS":
            # Get customer's recent payments
            payments = get_payments_for_customer(customer_id)
            if payments:
                # Return most recent payment
                latest_payment = max(payments, key=lambda x: x["date"])
                response_data = ResponseBuilder.build_payment_response(latest_payment)
            else:
                response_data = ResponseBuilder.build_text_response(
                    "No payment history found."
                )
        
        elif intent.value == "COMPLAINT":
            response_data = ResponseBuilder.build_text_response(
                "I understand you have a concern. Please describe the issue and I'll escalate it to our complaints team."
            )
            agent_status = "escalation_pending"
        
        elif intent.value == "GENERAL_INQUIRY":
            response_data = ResponseBuilder.build_text_response(
                "How can I help you with your LibertyAI insurance today? I can assist with policy information, claim status, payments, or complaints."
            )
        
        else:
            # Unknown or low confidence - escalate
            response_data = ResponseBuilder.build_handoff_response(
                reason="LOW_CONFIDENCE",
                queue="GENERAL"
            )
            conversation_status = ConversationStatus.HANDOFF
            next_action = NextActionType.ESCALATION
    
    # Add response to conversation
    state.add_message("assistant", response_data.get("text", ""))
    
    return SendMessageResponse(
        conversation_id=conversation_id,
        status=conversation_status,
        language={
            "code": language_code,
            "confidence": language_confidence
        },
        intent={
            "name": intent,
            "confidence": intent_confidence
        },
        authentication={
            "required": auth_required,
            "status": auth_status
        },
        agent={
            "name": agent_name,
            "status": agent_status
        },
        response=response_data or {},
        sources=[],
        next_action={
            "type": next_action,
            "reason": None
        }
    )


@app.get("/")
def root():
    """Root endpoint - API documentation"""
    return {
        "message": "Welcome to LibertyAI Assist API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "create_conversation": "POST /api/v1/conversations",
            "get_conversation": "GET /api/v1/conversations/{conversation_id}",
            "send_message": "POST /api/v1/conversations/{conversation_id}/messages"
        }
    }
