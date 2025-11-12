#!/usr/bin/env python3
"""
FastAPI server for contextual search of business angel profiles
Uses FAISS for fast embedding-based search and GPT-4o-mini for reranking

Usage:
    1. Set OPENAI_API_KEY environment variable
    2. Place your profiles JSON file (default: angel_profiles.json) in the same directory
    3. Run: python search_server.py
    4. Or: uvicorn search_server:app --reload

API Endpoints:
    - POST /search - Search with query, filters, and max_results
    - GET /search/get - Same as POST but with query parameters
    - GET /profiles - List all profiles with pagination
    - GET /profiles/{id} - Get a specific profile by index
    - GET /health - Health check
    - GET / - Server info

Example search request:
    POST /search
    {
        "query": "Find investors interested in fintech",
        "max_results": 10,
        "filters": {
            "is_investor": true,
            "sectors_of_interest": ["fintech", "ai"]
        }
    }
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

import faiss
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Angel Profile Search API",
    description="Fast contextual search for business angel profiles using FAISS and GPT reranking",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
profiles: List[Dict[str, Any]] = []
faiss_index: Optional[faiss.Index] = None
embedding_model = "text-embedding-3-small"
rerank_model = "gpt-4o-mini"  # Using gpt-4o-mini as gpt-5-nano may not be available
openai_client: Optional[OpenAI] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query/prompt")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter criteria for profiles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find investors interested in fintech and early stage startups",
                "max_results": 10,
                "filters": {
                    "is_investor": True,
                    "sectors_of_interest": ["fintech"],
                    "investment_stage": ["seed", "pre-seed"]
                }
            }
        }


class SearchResponse(BaseModel):
    """Search response model"""
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total number of results found")
    query: str = Field(..., description="Original search query")


def get_text_representation(profile: Dict[str, Any]) -> str:
    """
    Convert a profile to a text representation for embedding
    
    Args:
        profile: Profile dictionary
        
    Returns:
        Combined text representation of the profile
    """
    parts = []
    
    # Basic info
    if profile.get('name'):
        parts.append(f"Name: {profile['name']}")
    
    personal = profile.get('personal_info', {})
    if personal.get('headline'):
        parts.append(f"Headline: {personal['headline']}")
    if personal.get('location'):
        parts.append(f"Location: {personal['location']}")
    if personal.get('current_role'):
        parts.append(f"Current Role: {personal['current_role']}")
    if personal.get('company'):
        parts.append(f"Company: {personal['company']}")
    if personal.get('summary'):
        parts.append(f"Summary: {personal['summary']}")
    
    # Experience
    experience = personal.get('experience', [])
    if experience:
        exp_text = "Experience: " + "; ".join([
            f"{exp.get('title', '')} at {exp.get('company', '')}" 
            for exp in experience[:5]  # Limit to top 5
        ])
        parts.append(exp_text)
    
    # Education
    education = personal.get('education', [])
    if education:
        edu_text = "Education: " + "; ".join([
            f"{edu.get('degree', '')} from {edu.get('school', '')}"
            for edu in education[:3]  # Limit to top 3
        ])
        parts.append(edu_text)
    
    # Investment profile
    investment = profile.get('investment_profile', {})
    if investment.get('is_investor'):
        parts.append("Is an investor")
    if investment.get('investment_role'):
        parts.append(f"Investment Role: {investment['investment_role']}")
    if investment.get('investment_focus'):
        parts.append(f"Investment Focus: {', '.join(investment['investment_focus'])}")
    if investment.get('portfolio_companies'):
        parts.append(f"Portfolio Companies: {', '.join(investment['portfolio_companies'][:10])}")
    if investment.get('sectors_of_interest'):
        parts.append(f"Sectors of Interest: {', '.join(investment['sectors_of_interest'])}")
    if investment.get('investment_stage'):
        parts.append(f"Investment Stage: {', '.join(investment['investment_stage'])}")
    
    return " | ".join(parts)


def create_embeddings(texts: List[str]) -> np.ndarray:
    """
    Create embeddings for a list of texts using OpenAI
    
    Args:
        texts: List of text strings
        
    Returns:
        Numpy array of embeddings
    """
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized")
    
    try:
        response = openai_client.embeddings.create(
            model=embedding_model,
            input=texts
        )
        embeddings = [item.embedding for item in response.data]
        return np.array(embeddings).astype('float32')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embeddings: {str(e)}")


def matches_filters(profile: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """
    Check if a profile matches the given filters
    
    Args:
        profile: Profile dictionary
        filters: Filter criteria
        
    Returns:
        True if profile matches all filters
    """
    if not filters:
        return True
    
    for key, value in filters.items():
        # Handle nested keys (e.g., "personal_info.location")
        if '.' in key:
            parts = key.split('.')
            profile_value = profile
            for part in parts:
                if isinstance(profile_value, dict):
                    profile_value = profile_value.get(part)
                else:
                    profile_value = None
                    break
        else:
            # Check direct keys first
            profile_value = profile.get(key)
            
            # If not found, check in personal_info
            if profile_value is None:
                profile_value = profile.get('personal_info', {}).get(key)
            
            # If still not found, check in investment_profile
            if profile_value is None:
                profile_value = profile.get('investment_profile', {}).get(key)
        
        # Handle different filter types
        if value is None:
            # Filter for None/null values
            if profile_value is not None:
                return False
        elif isinstance(value, bool):
            # Boolean filter
            if profile_value != value:
                return False
        elif isinstance(value, list):
            # List filter (check if any value in filter list matches profile)
            if isinstance(profile_value, list):
                # Check if any item in filter value is in profile_value list
                # Case-insensitive comparison
                profile_lower = [str(p).lower() for p in profile_value]
                filter_lower = [str(f).lower() for f in value]
                if not any(f in profile_lower for f in filter_lower):
                    return False
            elif isinstance(profile_value, str):
                # Check if profile_value contains any of the filter values (case-insensitive)
                profile_lower = profile_value.lower()
                if not any(str(item).lower() in profile_lower for item in value):
                    return False
            else:
                # Profile value is not a list, check if it matches any filter value
                if profile_value is None or str(profile_value).lower() not in [str(v).lower() for v in value]:
                    return False
        elif isinstance(value, str):
            # String filter (case-insensitive partial match)
            if not profile_value or value.lower() not in str(profile_value).lower():
                return False
        else:
            # Exact match
            if profile_value != value:
                return False
    
    return True


def rerank_results(query: str, results: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
    """
    Rerank search results using GPT-5-nano (or gpt-4o-mini) based on query relevance
    
    Args:
        query: Original search query
        results: List of profile dictionaries to rerank
        max_results: Maximum number of results to return
        
    Returns:
        Reranked list of profiles
    """
    if not results:
        return []
    
    if not openai_client:
        # If no OpenAI client, return results as-is
        return results[:max_results]
    
    try:
        # Create a prompt for reranking
        profiles_text = []
        for i, profile in enumerate(results):
            text = get_text_representation(profile)
            profiles_text.append(f"Profile {i+1}:\n{text}")
        
        rerank_prompt = f"""You are a search ranking expert. Given a user query and a list of business angel profiles, rank the profiles by relevance to the query.

User Query: {query}

Profiles:
{chr(10).join(profiles_text)}

Please return a JSON object with a 'ranking' field containing an array of profile indices (0-based) ranked from most relevant to least relevant.

Example format: {{"ranking": [2, 0, 5, 1, 3, 4]}}"""

        response = openai_client.chat.completions.create(
            model=rerank_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that ranks search results by relevance. Return only a JSON object with a 'ranking' field containing an array of profile indices (0-based) from most to least relevant."},
                {"role": "user", "content": rerank_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        content = response.choices[0].message.content
        # Try to extract array from JSON
        try:
            result_json = json.loads(content)
            # Handle different response formats
            if isinstance(result_json, dict):
                # Look for common keys
                ranked_indices = result_json.get('ranking') or result_json.get('ranked_indices') or result_json.get('indices')
                if not ranked_indices:
                    # Try to find any array in the response
                    for key, value in result_json.items():
                        if isinstance(value, list):
                            ranked_indices = value
                            break
            else:
                ranked_indices = result_json
            
            if not isinstance(ranked_indices, list):
                # Fallback: return original order
                return results[:max_results]
            
            # Validate indices are within range
            valid_indices = [i for i in ranked_indices if isinstance(i, int) and 0 <= i < len(results)]
            
            if not valid_indices:
                # If no valid indices, return original order
                return results[:max_results]
            
            # Reorder results based on ranking
            reranked = [results[i] for i in valid_indices]
            # Add any missing results that weren't in the ranking
            ranked_set = set(valid_indices)
            for i, result in enumerate(results):
                if i not in ranked_set:
                    reranked.append(result)
            
            return reranked[:max_results]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # If parsing fails, return original order
            print(f"Error parsing rerank response: {e}, content: {content}")
            return results[:max_results]
            
    except Exception as e:
        print(f"Error during reranking: {e}")
        # Return original results if reranking fails
        return results[:max_results]


def load_profiles_from_json(json_path: str) -> List[Dict[str, Any]]:
    """
    Load profiles from a JSON file
    
    Args:
        json_path: Path to JSON file
        
    Returns:
        List of profile dictionaries
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        if not isinstance(profiles, list):
            raise ValueError("JSON file must contain a list of profiles")
        return profiles
    except FileNotFoundError:
        raise FileNotFoundError(f"Profile file not found: {json_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {json_path}: {e}")


def initialize_faiss_index(profiles: List[Dict[str, Any]]):
    """
    Initialize FAISS index with profile embeddings
    
    Args:
        profiles: List of profile dictionaries
    """
    global faiss_index
    
    if not profiles:
        print("Warning: No profiles to index")
        return
    
    print(f"Creating embeddings for {len(profiles)} profiles...")
    
    # Create text representations
    texts = [get_text_representation(profile) for profile in profiles]
    
    # Create embeddings
    embeddings = create_embeddings(texts)
    
    # Get embedding dimension
    dimension = embeddings.shape[1]
    
    # Create FAISS index (using L2 distance)
    faiss_index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    faiss_index.add(embeddings)
    
    print(f"FAISS index created with {faiss_index.ntotal} vectors of dimension {dimension}")


@app.on_event("startup")  # For FastAPI < 0.100, use lifespan for newer versions
async def startup_event():
    """Initialize the server on startup"""
    global profiles, openai_client
    
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. Embedding and reranking features will not work.")
    else:
        openai_client = OpenAI(api_key=api_key)
    
    # Load profiles from JSON file
    # Default to 'angel_profiles.json' or 'angel_profiles_llm.json'
    json_file = os.getenv("PROFILES_JSON", "angel_profiles.json")
    
    # Try multiple possible file names
    possible_files = [
        json_file,
        "angel_profiles.json",
        "angel_profiles_llm.json"
    ]
    
    loaded = False
    for file_path in possible_files:
        if os.path.exists(file_path):
            try:
                profiles = load_profiles_from_json(file_path)
                print(f"Loaded {len(profiles)} profiles from {file_path}")
                loaded = True
                break
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
    
    if not loaded:
        print("Warning: No profile JSON file found. Server will start but search will not work.")
        print("Please create a JSON file with profiles or set PROFILES_JSON environment variable.")
        profiles = []
        return
    
    # Initialize FAISS index
    if openai_client:
        initialize_faiss_index(profiles)
    else:
        print("Warning: Cannot create FAISS index without OpenAI API key")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Angel Profile Search API",
        "version": "1.0.0",
        "profiles_loaded": len(profiles),
        "faiss_index_ready": faiss_index is not None and faiss_index.ntotal > 0
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "profiles_count": len(profiles),
        "index_ready": faiss_index is not None and faiss_index.ntotal > 0 if faiss_index else False
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for profiles using embedding-based search with filtering and reranking
    
    Args:
        request: Search request with query, max_results, and filters
        
    Returns:
        Search results with reranked profiles
    """
    if not profiles:
        raise HTTPException(status_code=503, detail="No profiles loaded. Please load profiles first.")
    
    if not faiss_index or faiss_index.ntotal == 0:
        raise HTTPException(status_code=503, detail="FAISS index not initialized. OpenAI API key required.")
    
    if not openai_client:
        raise HTTPException(status_code=503, detail="OpenAI client not initialized. OPENAI_API_KEY required.")
    
    try:
        # Create embedding for query
        query_embedding = create_embeddings([request.query])
        
        # Search in FAISS index (get more results than needed for filtering and reranking)
        k = min(request.max_results * 3, faiss_index.ntotal)  # Get 3x results for filtering/reranking
        distances, indices = faiss_index.search(query_embedding, k)
        
        # Get candidate profiles
        candidate_profiles = [profiles[idx] for idx in indices[0] if 0 <= idx < len(profiles)]
        
        # Apply filters
        if request.filters:
            filtered_profiles = [
                profile for profile in candidate_profiles
                if matches_filters(profile, request.filters)
            ]
        else:
            filtered_profiles = candidate_profiles
        
        # Rerank results using GPT
        reranked_profiles = rerank_results(request.query, filtered_profiles, request.max_results)
        
        return SearchResponse(
            results=reranked_profiles,
            total_found=len(reranked_profiles),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/search/get", response_model=SearchResponse)
async def search_get(
    query: str = Query(..., description="Search query/prompt"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    is_investor: Optional[bool] = Query(None, description="Filter by is_investor"),
    investment_role: Optional[str] = Query(None, description="Filter by investment_role"),
    location: Optional[str] = Query(None, description="Filter by location"),
    sectors: Optional[str] = Query(None, description="Comma-separated list of sectors"),
    investment_stage: Optional[str] = Query(None, description="Comma-separated list of investment stages")
):
    """
    GET endpoint for search (alternative to POST)
    """
    # Build filters from query parameters
    filters = {}
    if is_investor is not None:
        filters['is_investor'] = is_investor
    if investment_role:
        filters['investment_role'] = investment_role
    if location:
        filters['location'] = location
    if sectors:
        filters['sectors_of_interest'] = [s.strip() for s in sectors.split(',')]
    if investment_stage:
        filters['investment_stage'] = [s.strip() for s in investment_stage.split(',')]
    
    request = SearchRequest(
        query=query,
        max_results=max_results,
        filters=filters if filters else None
    )
    
    return await search(request)


@app.get("/profiles/{profile_id}")
async def get_profile(profile_id: int):
    """
    Get a specific profile by index
    
    Args:
        profile_id: Index of the profile in the loaded profiles list
        
    Returns:
        Profile dictionary
    """
    if not profiles:
        raise HTTPException(status_code=503, detail="No profiles loaded")
    
    if profile_id < 0 or profile_id >= len(profiles):
        raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")
    
    return profiles[profile_id]


@app.get("/profiles")
async def list_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List all profiles with pagination
    
    Args:
        skip: Number of profiles to skip
        limit: Maximum number of profiles to return
        
    Returns:
        List of profiles
    """
    if not profiles:
        raise HTTPException(status_code=503, detail="No profiles loaded")
    
    return {
        "profiles": profiles[skip:skip + limit],
        "total": len(profiles),
        "skip": skip,
        "limit": limit
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

