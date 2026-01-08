# 🚀 VerifyStack API

**Tagline:** *"Stripe for AI Agent Verification"*

Infrastructure that makes AI agents production-ready by solving the verification problem.

---

## 🎯 The Problem We Solve

- **89% of AI agents fail to reach production** (stuck at pilot phase)
- **Root cause:** *"If you can't verify a task, you can't reliably automate it"*
- **AI hallucinations** cost businesses millions in bad decisions
- **No reliable verification layer** exists in the AI stack

## ✅ Our Solution

Multi-layered verification infrastructure:
1. **Real-time web research** across multiple sources
2. **OSINT intelligence analysis** for cross-verification
3. **Credibility scoring** with 6-factor assessment
4. **Confidence scores** (0.0 - 1.0) for every claim

---

## 🏗️ Architecture

```
┌─────────────────┐
│   AI Agent      │
│  (Your App)     │
└────────┬────────┘
         │
         │ HTTP POST
         │ X-API-Key: vsk_...
         │
┌────────▼────────┐
│ VerifyStack API │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Research│ │ OSINT │
│Engine │ │Engine │
└───┬───┘ └──┬────┘
    │        │
    └────┬───┘
         │
┌────────▼──────────┐
│ Intelligence      │
│ Credibility Score │
└───────────────────┘
         │
    Confidence Score
       0.0 - 1.0
```

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Run the server
python verify_api.py
```

Server runs on `http://localhost:8080`

### 2. Get Your API Key

Demo key is printed on startup:
```
🔑 Demo API Key: vsk_demo_xxxxxxxxxxxxx
```

### 3. Make Your First Verification

**Python:**
```python
import requests

API_KEY = "vsk_demo_xxxxxxxxxxxxx"

response = requests.post(
    "http://localhost:8080/api/v1/verify",
    headers={"X-API-Key": API_KEY},
    json={
        "claim": "Python is the most popular programming language in 2026",
        "verification_level": "standard"
    }
)

result = response.json()
print(f"Confidence: {result['confidence_score']}")
print(f"Status: {result['status']}")
print(f"Reasoning: {result['reasoning']}")
```

**JavaScript:**
```javascript
const API_KEY = "vsk_demo_xxxxxxxxxxxxx";

const response = await fetch("http://localhost:8080/api/v1/verify", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    },
    body: JSON.stringify({
        claim: "Python is the most popular programming language in 2026",
        verification_level: "standard"
    })
});

const result = await response.json();
console.log(`Confidence: ${result.confidence_score}`);
console.log(`Status: ${result.status}`);
```

**cURL:**
```bash
curl -X POST http://localhost:8080/api/v1/verify \
  -H "X-API-Key: vsk_demo_xxxxxxxxxxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "Python is the most popular programming language in 2026",
    "verification_level": "standard"
  }'
```

---

## 📚 API Reference

### Base URL
```
http://localhost:8080/api/v1
```

### Authentication
All endpoints require API key in header:
```
X-API-Key: vsk_demo_xxxxxxxxxxxxx
```

---

### `POST /verify`

Verify a claim with multi-layered verification.

**Request Body:**
```json
{
  "claim": "The statement to verify",
  "context": "Optional additional context",
  "sources": ["optional", "source", "urls"],
  "verification_level": "fast|standard|deep",
  "async_mode": false,
  "webhook_url": null,
  "metadata": {}
}
```

**Verification Levels:**
- `fast`: 1 credit, 1-2 sources, <2s response
- `standard`: 3 credits, 3-5 sources, 2-5s response (default)
- `deep`: 10 credits, 10+ sources, 5-30s response

**Response:**
```json
{
  "verification_id": "ver_abc123",
  "claim": "The statement to verify",
  "confidence_score": 0.85,
  "status": "verified",
  "evidence": {
    "supporting_sources": [
      {
        "url": "https://example.com",
        "title": "Source Title",
        "credibility": 0.90,
        "relevance": 0.88,
        "semantic_similarity": 0.75
      }
    ],
    "conflicting_sources": [],
    "neutral_sources": [],
    "credibility_breakdown": {
      "source_credibility": 0.315,
      "semantic_alignment": 0.27,
      "source_quantity": 0.10,
      "osint_quality": 0.165
    },
    "osint_intelligence": {}
  },
  "reasoning": "Claim verified with high confidence. Found 5 supporting sources with average credibility of 0.85.",
  "sources_analyzed": 5,
  "processing_time_ms": 3456,
  "verification_level": "standard",
  "timestamp": "2026-01-08T10:30:00Z",
  "credits_used": 3
}
```

**Status Codes:**
- `200 OK`: Verification completed
- `401 Unauthorized`: Invalid API key
- `402 Payment Required`: Insufficient credits
- `429 Too Many Requests`: Rate limit exceeded

---

### `GET /verification/{verification_id}`

Retrieve a previous verification by ID.

**Response:** Same as `/verify` endpoint

---

### `GET /usage`

Get usage statistics for your API key.

**Response:**
```json
{
  "api_key": "vsk_demo_...",
  "total_verifications": 42,
  "credits_remaining": 9874,
  "credits_used_today": 15,
  "rate_limit_remaining": 95,
  "billing_cycle_start": "2026-01-01T00:00:00Z",
  "billing_cycle_end": "2026-01-31T23:59:59Z"
}
```

---

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T10:30:00Z",
  "engines": {
    "intelligence": "operational",
    "osint": "operational",
    "research": "operational"
  }
}
```

---

## 💰 Pricing

### Free Tier
- **10,000 credits/month** (free forever)
- 100 requests/hour
- All verification levels
- Community support

**Perfect for:** Individual developers, side projects, testing

### Pro Tier - $99/month
- **100,000 credits/month**
- 1,000 requests/hour
- Priority verification (faster)
- Email support
- Custom webhooks

**Perfect for:** Startups, small teams, production apps

### Enterprise - Custom Pricing
- **Unlimited credits**
- Unlimited requests
- Dedicated infrastructure
- 99.99% SLA guarantee
- 24/7 support
- Custom integrations
- On-premise deployment

**Perfect for:** Large companies, high-volume applications

---

## 🎯 Use Cases

### 1. AI Agent Verification
```python
# Before executing a critical action, verify the decision
decision = agent.make_decision()
verification = verify_claim(decision)

if verification['confidence_score'] > 0.75:
    agent.execute(decision)
else:
    agent.ask_human(decision, verification['reasoning'])
```

### 2. Fact-Checking Content Generation
```python
# Verify AI-generated content before publishing
content = gpt4.generate_article(topic)
claims = extract_claims(content)

for claim in claims:
    result = verify_claim(claim)
    if result['status'] == 'unverified':
        flag_for_review(claim, result)
```

### 3. Research Validation
```python
# Validate research findings
finding = "Market size is $100B by 2030"
verification = verify_claim(finding, context="OSINT market")

report.add_finding(
    finding,
    confidence=verification['confidence_score'],
    sources=verification['evidence']['supporting_sources']
)
```

### 4. News/Misinformation Detection
```python
# Check news claims in real-time
news_claim = "Company X acquired Company Y for $10B"
result = verify_claim(news_claim, verification_level="fast")

if result['status'] == 'unverified':
    flag_as_potential_misinformation(news_claim)
```

---

## 🔧 Integration Patterns

### Pattern 1: Synchronous Verification
Best for: Real-time user interactions, <5s response needed
```python
result = verify_claim(claim, verification_level="fast")
return result['status']
```

### Pattern 2: Async with Webhooks
Best for: Batch processing, deep verification
```python
verify_claim(
    claim,
    verification_level="deep",
    async_mode=True,
    webhook_url="https://yourapp.com/webhook"
)
# Continue processing, receive webhook when done
```

### Pattern 3: Batch Verification
Best for: Content moderation, bulk fact-checking
```python
claims = extract_all_claims(document)
results = [verify_claim(c, "fast") for c in claims]
flagged = [r for r in results if r['confidence_score'] < 0.5]
```

---

## 📊 Understanding Confidence Scores

**Confidence Score Range:**
- `0.75 - 1.0`: **VERIFIED** - High confidence, multiple credible sources
- `0.40 - 0.75`: **UNCERTAIN** - Medium confidence, mixed or limited evidence
- `0.0 - 0.40`: **UNVERIFIED** - Low confidence, insufficient or conflicting evidence

**Confidence Breakdown:**
- **source_credibility** (35%): Average credibility of sources (domain authority, content quality)
- **semantic_alignment** (30%): How well sources support the claim
- **source_quantity** (15%): Number of sources analyzed
- **osint_quality** (20%): OSINT intelligence score (network analysis, patterns)

---

## 🛠️ Developer Dashboard

Open `verify_dashboard.html` in your browser for:
- ✅ API key management
- ✅ Usage statistics
- ✅ Live API testing
- ✅ Code examples
- ✅ Billing information

```bash
# Serve the dashboard
python -m http.server 3000

# Open in browser
# http://localhost:3000/verify_dashboard.html
```

---

## 🚦 Rate Limits

| Tier | Requests/Hour | Requests/Day | Requests/Month |
|------|---------------|--------------|----------------|
| Free | 100 | 2,400 | 72,000 |
| Pro | 1,000 | 24,000 | 720,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

---

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for API keys
3. **Rotate keys regularly** (every 90 days)
4. **Use separate keys** for dev/staging/production
5. **Monitor usage** for unusual patterns

```bash
# Good: Use environment variables
export VERIFYSTACK_API_KEY="vsk_prod_xxxxx"

# Bad: Hardcode in source
API_KEY = "vsk_prod_xxxxx"  # ❌ Don't do this!
```

---

## 📈 Scaling Tips

### For High Volume (>10k requests/day):

1. **Use async mode** with webhooks for deep verifications
2. **Implement caching** for frequently verified claims
3. **Batch similar claims** to reduce API calls
4. **Use "fast" level** for user-facing features
5. **Use "deep" level** only for critical decisions

### Example Caching:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def verify_with_cache(claim):
    return verify_claim(claim, "standard")
```

---

## 🌟 Competitive Advantage

| Feature | VerifyStack | Traditional OSINT | LLMs Only |
|---------|-------------|-------------------|-----------|
| Real-time verification | ✅ | ❌ | ❌ |
| Credibility scoring | ✅ | Partial | ❌ |
| Source attribution | ✅ | ✅ | ❌ |
| Semantic analysis | ✅ | ❌ | ✅ |
| API-first | ✅ | ❌ | ✅ |
| Multi-factor confidence | ✅ | ❌ | ❌ |
| Cost | $0.01-0.05/verify | $10k+/year | Free but unreliable |

---

## 🎓 Example Projects

### 1. AI Fact-Checker Bot
Verify claims in social media posts automatically
```python
for post in monitor_social_media():
    claims = extract_claims(post.text)
    for claim in claims:
        result = verify_claim(claim, "fast")
        if result['status'] == 'unverified':
            post.flag_for_review()
```

### 2. Content Quality Gate
Block AI-generated content with unverified claims
```python
article = generate_article(topic)
claims = extract_factual_claims(article)
unverified = [c for c in claims if verify_claim(c)['confidence_score'] < 0.6]

if unverified:
    return "Article contains unverified claims", unverified
else:
    publish(article)
```

### 3. Research Assistant
Auto-verify research findings with sources
```python
findings = conduct_research(topic)
verified_findings = [
    {
        **finding,
        "verification": verify_claim(finding['claim'], "deep")
    }
    for finding in findings
]
```

---

## 📞 Support

- **Documentation:** [docs.verifystack.ai](http://docs.verifystack.ai) *(coming soon)*
- **Email:** support@verifystack.ai
- **Discord:** [discord.gg/verifystack](http://discord.gg/verifystack) *(coming soon)*
- **GitHub:** [github.com/verifystack/api](http://github.com/verifystack/api)

---

## 🚀 Roadmap

### Q1 2026
- ✅ Core verification API (DONE)
- ✅ Developer dashboard (DONE)
- [ ] Python SDK
- [ ] JavaScript SDK
- [ ] Webhook support

### Q2 2026
- [ ] Real-time streaming verification
- [ ] Custom credibility models
- [ ] Multi-language support
- [ ] GraphQL API

### Q3 2026
- [ ] Blockchain verification layer
- [ ] Decentralized source network
- [ ] AI model fine-tuning on verified data
- [ ] Enterprise on-premise deployment

---

## 💡 The Vision

**We're building the trust layer for AI.**

Just like Stripe made payments simple, we're making verification simple.

Every AI agent will soon integrate VerifyStack to move from pilot to production.

**Join us in making AI actually reliable.** 🚀

---

## 📄 License

MIT License - See LICENSE file for details

---

**Built with ❤️ to solve the 11% problem**

*"If you can't verify a task, you can't reliably automate it." - Now you can.*
