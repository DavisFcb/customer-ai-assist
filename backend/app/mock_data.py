from datetime import datetime, timedelta
from typing import Dict, List, Any

# Mock Customers
CUSTOMERS = {
    "8001015009087": {
        "id": "8001015009087",
        "name": "Thabo Ndlela",
        "email": "thabo.ndlela@example.com",
        "phone": "+27821234567",
        "verified": True,
        "policies": ["POL-4439281", "POL-4439282"],
        "created_at": "2024-01-15"
    },
    "9205201234567": {
        "id": "9205201234567",
        "name": "Naledi Khumalo",
        "email": "naledi.khumalo@example.com",
        "phone": "+27829876543",
        "verified": True,
        "policies": ["POL-4439283", "POL-4439284"],
        "created_at": "2023-06-20"
    },
    "8512081234567": {
        "id": "8512081234567",
        "name": "Sipho Mthembu",
        "email": "sipho.mthembu@example.com",
        "phone": "+27837654321",
        "verified": False,
        "policies": ["POL-4439285"],
        "created_at": "2025-02-10"
    },
    "5612095944082": {
        "id": "5612095944082",
        "name": "Lindiwe Dlamini",
        "email": "lindiwe.dlamini@example.com",
        "phone": "+27603632360",
        "verified": True,
        "policies": ["POL-4439286"],
        "created_at": "2024-11-05"
    }
}

# Mock Policies
POLICIES = {
    "POL-4439281": {
        "policy_number": "POL-4439281",
        "customer_id": "8001015009087",
        "product": "Funeral Cover",
        "status": "ACTIVE",
        "start_date": "2023-03-01",
        "premium": 450.00,
        "premium_due": "2026-09-01",
        "cover_amount": 50000.00,
        "beneficiary": "Estate"
    },
    "POL-4439282": {
        "policy_number": "POL-4439282",
        "customer_id": "8001015009087",
        "product": "Life Insurance",
        "status": "ACTIVE",
        "start_date": "2022-06-15",
        "premium": 1200.00,
        "premium_due": "2026-09-15",
        "cover_amount": 500000.00,
        "beneficiary": "Wife - Naledi Ndlela"
    },
    "POL-4439283": {
        "policy_number": "POL-4439283",
        "customer_id": "9205201234567",
        "product": "Funeral Cover",
        "status": "ACTIVE",
        "start_date": "2024-01-01",
        "premium": 350.00,
        "premium_due": "2026-09-01",
        "cover_amount": 40000.00,
        "beneficiary": "Son - Themba Khumalo"
    },
    "POL-4439284": {
        "policy_number": "POL-4439284",
        "customer_id": "9205201234567",
        "product": "Income Protection",
        "status": "CANCELLED",
        "start_date": "2023-05-01",
        "end_date": "2025-12-31",
        "premium": 800.00,
        "cover_amount": 15000.00,
        "reason_cancelled": "Switched to alternative plan"
    },
    "POL-4439286": {
        "policy_number": "POL-4439286",
        "customer_id": "5612095944082",
        "product": "Funeral Cover",
        "status": "ACTIVE",
        "start_date": "2024-11-05",
        "premium": 300.00,
        "premium_due": "2026-09-05",
        "cover_amount": 30000.00,
        "beneficiary": "Daughter - Zanele Dlamini"
    },
    "POL-4439285": {
        "policy_number": "POL-4439285",
        "customer_id": "8512081234567",
        "product": "Funeral Cover",
        "status": "PENDING_ACTIVATION",
        "start_date": "2025-08-17",
        "premium": 280.00,
        "premium_due": "2026-09-17",
        "cover_amount": 30000.00,
        "beneficiary": "Mother - Lindiwe Mthembu"
    }
}

# Mock Claims
CLAIMS = {
    "CLM-20491": {
        "claim_id": "CLM-20491",
        "policy_number": "POL-4439281",
        "customer_id": "8001015009087",
        "status": "UNDER_REVIEW",
        "claim_type": "Funeral Claim",
        "amount": 50000.00,
        "date_filed": "2026-08-10",
        "last_updated": "2026-08-14",
        "description": "Claim for funeral expenses",
        "stage": "Documentation Review"
    },
    "CLM-20492": {
        "claim_id": "CLM-20492",
        "policy_number": "POL-4439281",
        "customer_id": "8001015009087",
        "status": "APPROVED",
        "claim_type": "Funeral Claim",
        "amount": 25000.00,
        "date_filed": "2025-12-05",
        "approved_date": "2025-12-20",
        "last_updated": "2025-12-20",
        "description": "Previously approved claim",
        "stage": "Completed"
    },
    "CLM-20493": {
        "claim_id": "CLM-20493",
        "policy_number": "POL-4439282",
        "customer_id": "8001015009087",
        "status": "REJECTED",
        "claim_type": "Life Insurance Claim",
        "amount": 500000.00,
        "date_filed": "2026-01-15",
        "rejected_date": "2026-02-10",
        "last_updated": "2026-02-10",
        "description": "Claim rejected - policy exclusion",
        "rejection_reason": "High-risk activities exclusion clause",
        "stage": "Completed"
    },
    "CLM-20494": {
        "claim_id": "CLM-20494",
        "policy_number": "POL-4439283",
        "customer_id": "9205201234567",
        "status": "PENDING_INFO",
        "claim_type": "Funeral Claim",
        "amount": 40000.00,
        "date_filed": "2026-07-20",
        "last_updated": "2026-08-01",
        "description": "Awaiting death certificate",
        "stage": "Awaiting Customer Documentation",
        "required_documents": ["Death Certificate", "Bank Account Details"]
    }
}

# Mock Payments
PAYMENTS = {
    "PAY-001": {
        "payment_id": "PAY-001",
        "policy_number": "POL-4439281",
        "customer_id": "8001015009087",
        "amount": 450.00,
        "date": "2026-08-01",
        "status": "PAID",
        "method": "Direct Debit",
        "reference": "DD-LIBERTY-202608"
    },
    "PAY-002": {
        "payment_id": "PAY-002",
        "policy_number": "POL-4439282",
        "customer_id": "8001015009087",
        "amount": 1200.00,
        "date": "2026-08-15",
        "status": "PENDING",
        "method": "Card",
        "due_date": "2026-09-15"
    },
    "PAY-003": {
        "payment_id": "PAY-003",
        "policy_number": "POL-4439283",
        "customer_id": "9205201234567",
        "amount": 350.00,
        "date": "2026-08-10",
        "status": "PAID",
        "method": "Bank Transfer",
        "reference": "TRF-LIBERTY-202608"
    },
    "PAY-004": {
        "payment_id": "PAY-004",
        "policy_number": "POL-4439281",
        "customer_id": "8001015009087",
        "amount": 450.00,
        "date": "2026-07-01",
        "status": "PAID",
        "method": "Direct Debit",
        "reference": "DD-LIBERTY-202607"
    }
}

# Mock Knowledge Documents (RAG)
KNOWLEDGE_DOCUMENTS = {
    "DOC-001": {
        "id": "DOC-001",
        "title": "Claim Rejection Procedures",
        "content": """
        When a claim is rejected, customers have the right to:
        1. Request a detailed explanation in writing within 15 days
        2. Appeal the decision within 30 days of rejection
        3. Involve the Ombudsman if dissatisfied with the appeal outcome
        
        Common rejection reasons include:
        - Policy exclusions not met (e.g., high-risk activities)
        - Claim filed outside the grace period
        - Incomplete documentation
        - Misrepresentation on application
        
        Customers can contact claims@libertyai.co.za for appeals.
        """,
        "category": "claims",
        "relevant_keywords": ["claim", "rejection", "appeal", "exclusion"]
    },
    "DOC-002": {
        "id": "DOC-002",
        "title": "Premium Payment Methods",
        "content": """
        LibertyAI Assist supports multiple payment methods:
        1. Direct Debit (recommended) - Automated monthly payments
        2. Bank Transfer - Manual monthly payments
        3. Card Payment - Visa, MasterCard, American Express
        4. Mobile Money - Airtime and other mobile platforms
        5. Cash Payment - Via authorized agents
        
        Payment can be made annually or monthly.
        Direct Debit customers enjoy a 5% discount.
        """,
        "category": "payments",
        "relevant_keywords": ["payment", "premium", "method", "direct debit"]
    },
    "DOC-003": {
        "id": "DOC-003",
        "title": "Policy Cancellation Rights",
        "content": """
        Customers have the right to cancel their policy:
        1. During the 31-day cooling-off period with full refund
        2. After the cooling-off period with 30 days' written notice
        
        If cancelled after cooling-off:
        - Partial refund based on unexpired period may apply
        - No penalties if no claims are pending
        
        To cancel, contact support@libertyai.co.za or call 0800-LIBERTY.
        """,
        "category": "policies",
        "relevant_keywords": ["cancel", "cancellation", "cooling-off", "refund"]
    },
    "DOC-004": {
        "id": "DOC-004",
        "title": "Complaint Procedures",
        "content": """
        We take complaints seriously. To lodge a complaint:
        1. Contact our complaints team at complaints@libertyai.co.za
        2. Provide details of your concern and policy number
        3. We will acknowledge within 24 hours
        4. Investigation takes 30 days maximum
        5. Formal response provided in writing
        
        If unsatisfied, escalate to:
        - The Ombudsman for Financial Services Provider (OFSP)
        - Phone: 012-346-1738
        - Email: info@faisombudsman.co.za
        """,
        "category": "complaints",
        "relevant_keywords": ["complaint", "concern", "issue", "ombudsman"]
    },
    "DOC-005": {
        "id": "DOC-005",
        "title": "Death Claim Process",
        "content": """
        When filing a death claim:
        1. Notify us immediately with policy number
        2. Provide the death certificate (certified copy)
        3. Provide funeral invoice or quotation
        4. Complete claim form with beneficiary details
        5. Provide ID proof of beneficiary
        
        Timeline:
        - Within 5 working days: We acknowledge receipt
        - Within 15 working days: We verify documentation
        - Within 30 working days: We settle approved claims
        
        Death claims must be filed within 12 months of death.
        """,
        "category": "claims",
        "relevant_keywords": ["death", "funeral", "claim", "certificate"]
    }
}

# Mock Complaints
COMPLAINTS = {
    "CMP-001": {
        "complaint_id": "CMP-001",
        "customer_id": "8001015009087",
        "date_filed": "2026-08-12",
        "status": "UNDER_REVIEW",
        "category": "Service Quality",
        "description": "Poor response time on claim status inquiries",
        "priority": "MEDIUM"
    },
    "CMP-002": {
        "complaint_id": "CMP-002",
        "customer_id": "9205201234567",
        "date_filed": "2026-07-20",
        "status": "RESOLVED",
        "category": "Billing",
        "description": "Incorrect premium amount charged",
        "priority": "HIGH",
        "resolution_date": "2026-08-05",
        "outcome": "Refunded R150 to customer"
    }
}


def get_customer(customer_id: str) -> Dict[str, Any] | None:
    """Get customer by ID"""
    return CUSTOMERS.get(customer_id)


def get_customer_by_phone(phone: str) -> Dict[str, Any] | None:
    """Get customer by phone number (used to map WhatsApp senders to an RSA ID)"""
    for customer in CUSTOMERS.values():
        if customer.get("phone") == phone:
            return customer
    return None


def get_policies_for_customer(customer_id: str) -> List[Dict[str, Any]]:
    """Get all policies for a customer"""
    customer = get_customer(customer_id)
    if not customer:
        return []
    return [POLICIES[p] for p in customer.get("policies", []) if p in POLICIES]


def get_claims_for_customer(customer_id: str) -> List[Dict[str, Any]]:
    """Get all claims for a customer"""
    return [c for c in CLAIMS.values() if c["customer_id"] == customer_id]


def get_payments_for_customer(customer_id: str) -> List[Dict[str, Any]]:
    """Get all payments for a customer"""
    return [p for p in PAYMENTS.values() if p["customer_id"] == customer_id]


def get_policy(policy_number: str) -> Dict[str, Any] | None:
    """Get policy by number"""
    return POLICIES.get(policy_number)


def get_claim(claim_id: str) -> Dict[str, Any] | None:
    """Get claim by ID"""
    return CLAIMS.get(claim_id)


def search_knowledge(keywords: List[str]) -> List[Dict[str, Any]]:
    """Search knowledge documents by keywords"""
    results = []
    keywords_lower = [k.lower() for k in keywords]
    
    for doc in KNOWLEDGE_DOCUMENTS.values():
        doc_keywords_lower = [kw.lower() for kw in doc["relevant_keywords"]]
        if any(kw in doc_keywords_lower for kw in keywords_lower):
            results.append(doc)
    
    return results
