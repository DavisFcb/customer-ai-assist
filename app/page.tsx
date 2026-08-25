'use client';

import React, { useState, useRef, useEffect } from 'react';

interface Message {
  id: number;
  sender: 'user' | 'bot';
  type: string;
  text: string;
  data?: Record<string, unknown>;
  time: string;
}

interface APIResponse {
  conversation_id: string;
  status: string;
  language: { code: string; confidence: number };
  intent: { name: string; confidence: number };
  authentication: { required: boolean; status: string };
  agent: { name: string; status: string };
  response: {
    type: string;
    text: string;
    data?: Record<string, unknown>;
  };
  sources: string[];
  next_action: { type: string; reason?: string };
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Component for rendering different message types
const MessageRenderer = ({ message }: { message: Message }) => {
  const getTimeString = () => {
    return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  switch (message.type) {
    case 'claim':
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble claim-card">
            <p>{message.text}</p>
            {message.data && (
              <div className="claim-details">
                <div className="detail-item">
                  <span className="label">Claim ID:</span>
                  <span className="value">{message.data.claim_id}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Status:</span>
                  <span className={`status ${String(message.data.status).toLowerCase()}`}>
                    {message.data.status}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="label">Last Updated:</span>
                  <span className="value">{message.data.last_updated}</span>
                </div>
                {message.data.stage && (
                  <div className="detail-item">
                    <span className="label">Stage:</span>
                    <span className="value">{message.data.stage}</span>
                  </div>
                )}
              </div>
            )}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );

    case 'policy':
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble policy-card">
            <p>{message.text}</p>
            {message.data && (
              <div className="policy-details">
                <div className="detail-item">
                  <span className="label">Policy #:</span>
                  <span className="value">{message.data.policy_number}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Product:</span>
                  <span className="value">{message.data.product}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Status:</span>
                  <span className={`status ${String(message.data.status).toLowerCase()}`}>
                    {message.data.status}
                  </span>
                </div>
                {message.data.premium && (
                  <div className="detail-item">
                    <span className="label">Premium:</span>
                    <span className="value">R{message.data.premium}</span>
                  </div>
                )}
              </div>
            )}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );

    case 'payment':
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble payment-card">
            <p>{message.text}</p>
            {message.data && (
              <div className="payment-details">
                <div className="detail-item">
                  <span className="label">Amount:</span>
                  <span className="value">R{message.data.amount}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Date:</span>
                  <span className="value">{message.data.date}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Status:</span>
                  <span className={`status ${String(message.data.status).toLowerCase()}`}>
                    {message.data.status}
                  </span>
                </div>
              </div>
            )}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );

    case 'verification':
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble verification-card">
            <p>{message.text}</p>
            {message.data && (
              <div className="verification-prompt">
                <p className="verification-text">
                  Please provide your ID number to continue securely.
                </p>
              </div>
            )}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );

    case 'handoff':
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble handoff-card">
            <p>{message.text}</p>
            {message.data && (
              <div className="handoff-info">
                <div className="detail-item">
                  <span className="label">Queue:</span>
                  <span className="value">{message.data.queue}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Reason:</span>
                  <span className="value">{message.data.reason}</span>
                </div>
                <button className="handoff-button">Connect to Consultant</button>
              </div>
            )}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );

    default:
      return (
        <div className={`message-row ${message.sender === 'user' ? 'outgoing' : 'incoming'}`}>
          <div className="message-bubble">
            {message.text.split('\n').map((line, idx) => (
              <span key={`${message.id}-${idx}`}>
                {line}
                {idx < message.text.split('\n').length - 1 && <br />}
              </span>
            ))}
            <div className="message-time">{getTimeString()}</div>
          </div>
        </div>
      );
  }
};

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: 'bot',
      type: 'text',
      text: "Hi! I'm LibertyAI Assist. How can I help you today?",
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [inputValue, setInputValue] = useState('');
  const [customerId, setCustomerId] = useState('8001015009087');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showIdInput, setShowIdInput] = useState(true);
  const chatBodyRef = useRef<HTMLDivElement>(null);

  // Initialize conversation
  useEffect(() => {
    const initializeConversation = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel: 'web', language: 'en' }),
        });

        if (response.ok) {
          const data = await response.json();
          setConversationId(data.conversation_id);
        }
      } catch (error) {
        console.error('Failed to initialize conversation:', error);
      }
    };

    initializeConversation();
  }, []);

  // Auto-scroll to latest message
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  const handleStartChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId.trim() || !conversationId) return;

    setShowIdInput(false);

    // Add user message
    const userMsg: Message = {
      id: messages.length + 1,
      sender: 'user',
      type: 'text',
      text: `My ID number is ${customerId}`,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);

    // Send to API
    await sendMessage(`Verify my identity with ID: ${customerId}`);
  };

  const sendMessage = async (text: string) => {
    if (!conversationId || !customerId) return;

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: { text },
          customer: { id_number: customerId },
          language: 'en',
          channel: 'web',
        }),
      });

      if (response.ok) {
        const data: APIResponse = await response.json();

        // Add bot response
        const botMsg: Message = {
          id: messages.length + 2,
          sender: 'bot',
          type: data.response.type,
          text: data.response.text,
          data: data.response.data,
          time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        const error = await response.json();
        console.error('API error:', error);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || !conversationId) return;

    const userMsg: Message = {
      id: messages.length + 1,
      sender: 'user',
      type: 'text',
      text: inputValue,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');

    await sendMessage(inputValue);
  };

  const handleQuickAction = async (action: string) => {
    const quickMessages: Record<string, string> = {
      'Check claim': 'Where is my claim?',
      'Policy details': 'Tell me about my policy',
      'Payment help': 'When is my payment due?',
      'Speak to agent': 'I need to speak with a consultant',
    };

    const message = quickMessages[action] || action;
    const userMsg: Message = {
      id: messages.length + 1,
      sender: 'user',
      type: 'text',
      text: message,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMsg]);

    await sendMessage(message);
  };

  const quickActions = ['Check claim', 'Policy details', 'Payment help', 'Speak to agent'];

  return (
    <main className="app-shell">
      <div className="phone-frame">
        <header className="chat-header">
          <div className="header-left">
            <button className="back-btn" aria-label="Back">
              &lt;
            </button>
            <div className="avatar">L</div>
            <div className="header-text">
              <h1>LibertyAI Assist</h1>
              <div className="status-row">
                <span className="status-dot" />
                <span>online / secure</span>
              </div>
            </div>
          </div>
          <div className="header-actions">
            <span>⋮</span>
          </div>
        </header>

        <div className="chat-body" ref={chatBodyRef}>
          {showIdInput ? (
            <form onSubmit={handleStartChat} className="id-input-form">
              <div className="id-input-container">
                <h2>Welcome to LibertyAI Assist</h2>
                <p>Please enter your ID number to get started</p>
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  placeholder="Enter your ID number"
                  className="id-input"
                />
                <button type="submit" className="start-button">
                  Start Chat
                </button>
              </div>
            </form>
          ) : (
            <>
              {messages.map((message) => (
                <MessageRenderer key={message.id} message={message} />
              ))}

              {isLoading && (
                <div className="typing-row">
                  <div className="typing-bubble">
                    <span className="dot" />
                    <span className="dot" />
                    <span className="dot" />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {!showIdInput && (
          <>
            <div className="quick-actions">
              {quickActions.map((action) => (
                <button
                  key={action}
                  className="quick-pill"
                  onClick={() => handleQuickAction(action)}
                  disabled={isLoading}
                >
                  {action}
                </button>
              ))}
            </div>

            <form onSubmit={handleSendMessage} className="composer">
              <button type="button" className="emoji-button" aria-label="Add emoji">
                ☺
              </button>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type a message"
                disabled={isLoading}
              />
              <button type="submit" className="send-button" disabled={isLoading || !inputValue.trim()}>
                Send
              </button>
            </form>
          </>
        )}
      </div>
    </main>
  );
}
