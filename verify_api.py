#!/usr/bin/env python3
"""
VerifyStack API - Infrastructure for AI Agent Verification
"Stripe for AI Agent Verification"

The verification layer that makes AI agents production-ready.
"""

import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import our existing engines
from intelligence_engine import IntelligenceEngine
from osint_engine import OSINTEngine
from research_engine import ResearchEngine, ResearchParameters


# ============================================================================
# API Models
# ============================================================================

class VerificationLevel(str, Enum):
    FAST = "fast"      # Quick checks, 1-2 sources, <2s
    STANDARD = "standard"  # Balanced, 3-5 sources, 2-5s
    DEEP = "deep"      # Comprehensive, 10+ sources, 5-30s


class VerificationStatus(str, Enum):
    VERIFIED = "verified"      # High confidence (>0.75)
    UNCERTAIN = "uncertain"    # Medium confidence (0.4-0.75)
    UNVERIFIED = "unverified"  # Low confidence (<0.4)
    PROCESSING = "processing"  # Async in progress
    FAILED = "failed"          # Error occurred


class VerifyRequest(BaseModel):
    claim: str = Field(..., description="The claim or statement to verify")
    context: Optional[str] = Field(None, description="Additional context for verification")
    sources: Optional[List[str]] = Field(None, description="Optional source URLs to check against")
    verification_level: VerificationLevel = Field(VerificationLevel.STANDARD, description="Verification depth")
    async_mode: bool = Field(False, description="Use async processing with webhooks")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for async results")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Custom metadata")


class Evidence(BaseModel):
    supporting_sources: List[Dict[str, Any]] = []
    conflicting_sources: List[Dict[str, Any]] = []
    neutral_sources: List[Dict[str, Any]] = []
    credibility_breakdown: Dict[str, float] = {}
    osint_intelligence: Dict[str, Any] = {}


class VerifyResponse(BaseModel):
    verification_id: str
    claim: str
    confidence_score: float  # 0.0 - 1.0
    status: VerificationStatus
    evidence: Evidence
    reasoning: str
    sources_analyzed: int
    processing_time_ms: int
    verification_level: VerificationLevel
    timestamp: str
    credits_used: int


class UsageStats(BaseModel):
    api_key: str
    total_verifications: int
    credits_remaining: int
    credits_used_today: int
    rate_limit_remaining: int
    billing_cycle_start: str
    billing_cycle_end: str


class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    credits: int
    rate_limit: int
    created_at: str


# ============================================================================
# In-Memory Storage (Replace with real DB in production)
# ============================================================================

class Storage:
    """Simple in-memory storage for MVP. Replace with PostgreSQL/Redis in production."""

    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self.verifications: Dict[str, Dict] = {}
        self.usage_stats: Dict[str, Dict] = {}

        # Create a demo API key
        demo_key = "vsk_demo_" + secrets.token_urlsafe(32)
        self.api_keys[demo_key] = {
            "name": "Demo Key",
            "credits": 10000,
            "rate_limit": 100,  # per hour
            "created_at": datetime.now().isoformat(),
            "tier": "free"
        }
        self.usage_stats[demo_key] = {
            "total_verifications": 0,
            "credits_used_today": 0,
            "last_reset": datetime.now().date().isoformat(),
            "hourly_requests": []
        }

        print(f"\n🔑 Demo API Key: {demo_key}")
        print(f"   Use this key in header: X-API-Key: {demo_key}\n")

    def validate_api_key(self, api_key: str) -> bool:
        return api_key in self.api_keys

    def use_credits(self, api_key: str, credits: int) -> bool:
        if api_key not in self.api_keys:
            return False

        key_data = self.api_keys[api_key]
        if key_data["credits"] < credits:
            return False

        key_data["credits"] -= credits

        # Update usage stats
        stats = self.usage_stats[api_key]
        stats["total_verifications"] += 1
        stats["credits_used_today"] += credits

        # Reset daily counter if needed
        today = datetime.now().date().isoformat()
        if stats["last_reset"] != today:
            stats["credits_used_today"] = credits
            stats["last_reset"] = today

        return True

    def check_rate_limit(self, api_key: str) -> bool:
        """Check if API key is within rate limits"""
        if api_key not in self.api_keys:
            return False

        stats = self.usage_stats[api_key]
        rate_limit = self.api_keys[api_key]["rate_limit"]

        # Clean old requests (older than 1 hour)
        now = time.time()
        stats["hourly_requests"] = [
            ts for ts in stats["hourly_requests"]
            if now - ts < 3600
        ]

        if len(stats["hourly_requests"]) >= rate_limit:
            return False

        stats["hourly_requests"].append(now)
        return True


# ============================================================================
# Verification Engine
# ============================================================================

class VerificationEngine:
    """Core verification engine that orchestrates intelligence and OSINT"""

    def __init__(self):
        self.intelligence_engine = IntelligenceEngine()
        self.osint_engine = OSINTEngine()
        self.research_engine = ResearchEngine()

    async def verify_claim(
        self,
        claim: str,
        context: Optional[str] = None,
        sources: Optional[List[str]] = None,
        level: VerificationLevel = VerificationLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Verify a claim using multi-layered verification:
        1. Research the claim across multiple sources
        2. Apply OSINT intelligence analysis
        3. Score credibility using intelligence engine
        4. Return confidence score with evidence
        """
        start_time = time.time()

        # Determine search depth based on level
        depth_map = {
            VerificationLevel.FAST: 2,
            VerificationLevel.STANDARD: 3,
            VerificationLevel.DEEP: 5
        }
        max_results_map = {
            VerificationLevel.FAST: 5,
            VerificationLevel.STANDARD: 10,
            VerificationLevel.DEEP: 20
        }

        # Build search query
        search_query = claim
        if context:
            search_query = f"{claim} {context}"

        # Phase 1: Research the claim
        params = ResearchParameters(
            query=search_query,
            depth=depth_map[level],
            max_results=max_results_map[level],
            relevance_threshold=0.3
        )

        await self.research_engine.research(params)

        # Get research results
        results = self.research_engine.results

        if not results:
            return {
                "confidence_score": 0.0,
                "status": VerificationStatus.UNVERIFIED,
                "evidence": {
                    "supporting_sources": [],
                    "conflicting_sources": [],
                    "neutral_sources": [],
                    "credibility_breakdown": {},
                    "osint_intelligence": {}
                },
                "reasoning": "No sources found to verify the claim.",
                "sources_analyzed": 0,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }

        # Phase 2: Analyze with intelligence engine
        documents = [
            {
                "text": f"{r.title} {r.summary} {r.content}",
                "title": r.title,
                "url": r.url,
                "metadata": r.metadata
            }
            for r in results
        ]

        # Semantic search for claim
        semantic_results = self.intelligence_engine.semantic_search(
            claim,
            documents,
            top_k=len(documents)
        )

        # Phase 3: Credibility scoring
        credibility_scores = []
        for result in results:
            score = self.intelligence_engine.score_credibility(
                url=result.url,
                title=result.title,
                content=result.content,
                metadata=result.metadata
            )
            credibility_scores.append({
                "url": result.url,
                "title": result.title,
                "credibility": score["overall_credibility"],
                "trust_level": score["trust_level"],
                "breakdown": score["breakdown"]
            })

        # Phase 4: OSINT analysis
        results_data = [r.to_dict() for r in results]
        osint_analysis = self.osint_engine.comprehensive_analysis(results_data)

        # Phase 5: Determine confidence and categorize sources
        supporting = []
        conflicting = []
        neutral = []

        avg_credibility = sum(s["credibility"] for s in credibility_scores) / len(credibility_scores)
        avg_relevance = sum(r.relevance_score for r in results) / len(results)

        # Categorize sources based on semantic similarity and sentiment
        for i, result in enumerate(results):
            semantic_score = semantic_results[i]["similarity"] if i < len(semantic_results) else 0
            credibility = credibility_scores[i]["credibility"]

            source_info = {
                "url": result.url,
                "title": result.title,
                "credibility": credibility,
                "relevance": result.relevance_score,
                "semantic_similarity": semantic_score
            }

            # High semantic similarity + high credibility = supporting
            if semantic_score > 0.6 and credibility > 0.6:
                supporting.append(source_info)
            # Low semantic similarity but found = conflicting
            elif semantic_score < 0.3:
                conflicting.append(source_info)
            else:
                neutral.append(source_info)

        # Calculate final confidence score
        confidence_factors = {
            "source_credibility": avg_credibility * 0.35,
            "semantic_alignment": (len(supporting) / len(results)) * 0.30,
            "source_quantity": min(len(results) / 10, 1.0) * 0.15,
            "osint_quality": osint_analysis.get("overall_quality", {}).get("intelligence_score", 0) * 0.20
        }

        confidence_score = sum(confidence_factors.values())
        confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp to 0-1

        # Determine status
        if confidence_score > 0.75:
            status = VerificationStatus.VERIFIED
            reasoning = f"Claim verified with high confidence. Found {len(supporting)} supporting sources with average credibility of {avg_credibility:.2f}."
        elif confidence_score > 0.4:
            status = VerificationStatus.UNCERTAIN
            reasoning = f"Claim partially verified with medium confidence. Mixed evidence from {len(results)} sources."
        else:
            status = VerificationStatus.UNVERIFIED
            reasoning = f"Claim unverified with low confidence. Insufficient supporting evidence found."

        if conflicting:
            reasoning += f" Warning: {len(conflicting)} sources present conflicting information."

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "confidence_score": round(confidence_score, 3),
            "status": status,
            "evidence": {
                "supporting_sources": supporting[:5],  # Top 5
                "conflicting_sources": conflicting[:5],
                "neutral_sources": neutral[:3],
                "credibility_breakdown": confidence_factors,
                "osint_intelligence": osint_analysis
            },
            "reasoning": reasoning,
            "sources_analyzed": len(results),
            "processing_time_ms": processing_time
        }


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="VerifyStack API",
    description="Infrastructure for AI Agent Verification - Make your AI agents production-ready",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
storage = Storage()
verification_engine = VerificationEngine()


# ============================================================================
# Dependencies
# ============================================================================

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Verify API key from header"""
    if not storage.validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not storage.check_rate_limit(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return x_api_key


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root - health check"""
    return {
        "service": "VerifyStack API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs",
        "tagline": "Stripe for AI Agent Verification"
    }


@app.post("/api/v1/verify", response_model=VerifyResponse)
async def verify_claim(
    request: VerifyRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """
    Verify a claim with multi-layered verification

    Returns confidence score, evidence, and reasoning
    """

    # Calculate credits needed
    credits_map = {
        VerificationLevel.FAST: 1,
        VerificationLevel.STANDARD: 3,
        VerificationLevel.DEEP: 10
    }
    credits_needed = credits_map[request.verification_level]

    # Check and use credits
    if not storage.use_credits(api_key, credits_needed):
        raise HTTPException(status_code=402, detail="Insufficient credits")

    # Generate verification ID
    verification_id = "ver_" + secrets.token_urlsafe(16)

    # Perform verification
    result = await verification_engine.verify_claim(
        claim=request.claim,
        context=request.context,
        sources=request.sources,
        level=request.verification_level
    )

    # Build response
    response = VerifyResponse(
        verification_id=verification_id,
        claim=request.claim,
        confidence_score=result["confidence_score"],
        status=result["status"],
        evidence=Evidence(**result["evidence"]),
        reasoning=result["reasoning"],
        sources_analyzed=result["sources_analyzed"],
        processing_time_ms=result["processing_time_ms"],
        verification_level=request.verification_level,
        timestamp=datetime.now().isoformat(),
        credits_used=credits_needed
    )

    # Store verification
    storage.verifications[verification_id] = response.dict()

    return response


@app.get("/api/v1/verification/{verification_id}")
async def get_verification(
    verification_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get a previous verification by ID"""
    if verification_id not in storage.verifications:
        raise HTTPException(status_code=404, detail="Verification not found")

    return storage.verifications[verification_id]


@app.get("/api/v1/usage", response_model=UsageStats)
async def get_usage(api_key: str = Depends(verify_api_key)):
    """Get usage statistics for your API key"""

    key_data = storage.api_keys[api_key]
    stats = storage.usage_stats[api_key]

    now = datetime.now()
    cycle_end = now + timedelta(days=30)

    return UsageStats(
        api_key=api_key[:20] + "...",  # Masked
        total_verifications=stats["total_verifications"],
        credits_remaining=key_data["credits"],
        credits_used_today=stats["credits_used_today"],
        rate_limit_remaining=key_data["rate_limit"] - len(stats["hourly_requests"]),
        billing_cycle_start=now.isoformat(),
        billing_cycle_end=cycle_end.isoformat()
    )


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": {
            "intelligence": "operational",
            "osint": "operational",
            "research": "operational"
        }
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 VerifyStack API - Infrastructure for AI Agent Verification")
    print("="*70)
    print("\n📊 Starting server on http://0.0.0.0:8080")
    print("📚 API Documentation: http://0.0.0.0:8080/docs")
    print("🔧 ReDoc: http://0.0.0.0:8080/redoc")
    print("\n" + "="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
