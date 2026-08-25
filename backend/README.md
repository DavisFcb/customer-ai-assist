# LibertyAI Assist Backend

A comprehensive mock FastAPI backend for LibertyAI Assist, an AI-powered insurance customer service platform with multi-channel support (Web, WhatsApp, Voice).

## Features

- **Multi-Channel Support**: Web, WhatsApp, and Voice integration
- **Multilingual Conversations**: Support for English, isiZulu, isiXhosa, and Afrikaans
- **Intent Detection**: Automatic classification of customer inquiries (claim status, policy info, payments, complaints)
- **Customer Authentication**: Secure verification before accessing sensitive information
- **Agent Routing**: Intelligent routing to specialized agents (Claims, Policies, Payments, Complaints)
- **RAG-Ready**: Knowledge base integration for grounded responses
- **Human Escalation**: Seamless handoff to human consultants when needed
- **Mock Data**: Comprehensive synthetic customer, policy, claim, and payment data

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Run the server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```
GET /health
```

### Create Conversation
```
POST /api/v1/conversations
Content-Type: application/json

{
  "channel": "web",
  "language": "en"
}

Response:
{
  "conversation_id": "conv_ABC123",
  "status": "active"
}
```

### Send Message
```
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json

{
  "message": {
    "text": "Where is my claim?"
  },
  "customer": {
    "id_number": "8001015009087"
  },
  "language": "en",
  "channel": "web"
}

Response:
{
  "conversation_id": "conv_ABC123",
  "status": "completed",
  "language": {
    "code": "en",
    "confidence": 0.99
  },
  "intent": {
    "name": "CLAIM_STATUS",
    "confidence": 0.96
  },
  "authentication": {
    "required": true,
    "status": "verified"
  },
  "agent": {
    "name": "claims",
    "status": "completed"
  },
  "response": {
    "type": "claim",
    "text": "Your claim is currently under review.",
    "data": {
      "claim_id": "CLM-20491",
      "status": "UNDER_REVIEW",
      "last_updated": "2026-08-14"
    }
  },
  "sources": [],
  "next_action": {
    "type": "none"
  }
}
```

### Get Conversation
```
GET /api/v1/conversations/{conversation_id}

Response:
{
  "conversation_id": "conv_ABC123",
  "status": "active",
  "channel": "web",
  "language": "en",
  "customer_id": "8001015009087",
  "messages": [...],
  "created_at": "2026-08-17T10:30:00",
  "updated_at": "2026-08-17T10:32:00"
}
```

## Response Types

The API supports multiple response types based on the customer's request:

### Text Response
```json
{
  "type": "text",
  "text": "Your premium is due on 1 September."
}
```

### Claim Response
```json
{
  "type": "claim",
  "text": "Your claim is currently under review.",
  "data": {
    "claim_id": "CLM-20491",
    "status": "UNDER_REVIEW",
    "last_updated": "2026-08-14"
  }
}
```

### Policy Response
```json
{
  "type": "policy",
  "text": "Your policy is active.",
  "data": {
    "policy_number": "POL-4439281",
    "product": "Funeral Cover",
    "status": "ACTIVE"
  }
}
```

### Payment Response
```json
{
  "type": "payment",
  "text": "Your latest premium payment was received.",
  "data": {
    "amount": 450.00,
    "date": "2026-08-01",
    "status": "PAID"
  }
}
```

### Verification Response
```json
{
  "type": "verification",
  "text": "Please verify your identity before I can provide those details.",
  "data": {
    "method": "id_number"
  }
}
```

### Handoff Response
```json
{
  "type": "handoff",
  "text": "I'll connect you with a consultant who can assist further.",
  "data": {
    "queue": "CLAIMS",
    "reason": "LOW_CONFIDENCE"
  }
}
```

## Mock Customers

Use these customer IDs for testing:

- **8001015009087** - Thabo Ndlela (Multiple policies and claims)
- **9205201234567** - Naledi Khumalo (Active policies)
- **8512081234567** - Sipho Mthembu (New customer, unverified)

## Supported Intents

- `CLAIM_STATUS`: Inquiries about claim status
- `POLICY_INFO`: Questions about active policies
- `PAYMENT_STATUS`: Payment history and due dates
- `COMPLAINT`: Customer complaints
- `GENERAL_INQUIRY`: General questions
- `UNKNOWN`: Low confidence matches

## Conversation States

- `active`: Conversation in progress
- `awaiting_verification`: Waiting for customer authentication
- `processing`: Processing customer request
- `completed`: Request completed
- `failed_verification`: Authentication failed
- `handoff`: Escalated to human agent

## Architecture

### Services (`app/services.py`)

- **IntentDetector**: Analyzes message to determine customer intent
- **LanguageDetector**: Detects message language
- **AuthenticationService**: Verifies customer identity
- **AgentRouter**: Routes intents to appropriate agents
- **RAGService**: Retrieves knowledge documents
- **ResponseBuilder**: Constructs API responses
- **ConversationState**: Manages conversation lifecycle

### Mock Data (`app/mock_data.py`)

- **Customers**: Sample customer profiles with verification status
- **Policies**: Insurance policies with various statuses
- **Claims**: Claims in different stages (review, approved, rejected)
- **Payments**: Payment history and status
- **Knowledge Documents**: RAG documents for grounded responses

## Integration with Frontend

The React frontend should:

1. Create a conversation via `POST /api/v1/conversations`
2. Send user messages via `POST /api/v1/conversations/{conversation_id}/messages`
3. Render components based on `response.type`:
   - `"text"`: Simple text message
   - `"claim"`: Claim status card
   - `"policy"`: Policy information card
   - `"payment"`: Payment details card
   - `"verification"`: Authentication prompt
   - `"handoff"`: Human escalation notice

## WhatsApp Integration

The WhatsApp channel should:

1. Receive messages from WhatsApp Business API
2. Call `POST /api/v1/conversations/{conversation_id}/messages` with channel="whatsapp"
3. Parse the response and send back via WhatsApp Business API
4. Handle rich media responses (cards for claim/policy/payment)

## Future Enhancements

- [ ] Integration with real Bedrock for AI responses
- [ ] Persistent database storage (replace in-memory conversations)
- [ ] Real WhatsApp Business API integration
- [ ] Voice transcription for voice channel
- [ ] Complete RAG implementation with embeddings
- [ ] Real authentication service (OAuth2, ID verification)
- [ ] Analytics and conversation monitoring
- [ ] Multi-agent conversations
- [ ] Callback scheduling for future escalations

## Development

### Running Tests
```bash
pytest
```

### Linting
```bash
pylint app/
```

### Code Formatting
```bash
black app/
```

## Support

For issues or questions about the backend API, refer to the interactive documentation at `/docs` or `/redoc`.
