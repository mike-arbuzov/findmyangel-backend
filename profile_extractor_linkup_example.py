#!/usr/bin/env python3
"""
Example usage of the LinkupProfileExtractor class
Demonstrates how to extract business angel profiles using Linkup.so API
"""

from profile_extractor_linkup import LinkupProfileExtractor, extract_angel_profile_linkup
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def example_single_profile():
    """Example: Extract a single profile using Linkup.so"""
    print("="*60)
    print("EXAMPLE 1: Extract Single Profile with Linkup.so")
    print("="*60)
    
    # Make sure LINKUP_API_KEY is set
    if not os.getenv("LINKUP_API_KEY"):
        print("Error: LINKUP_API_KEY environment variable not set!")
        print("Set it with: export LINKUP_API_KEY='your-api-key'")
        return None
    
    # Extract profile for a single business angel
    profile = extract_angel_profile_linkup(
        name="Mike Arbuzov",
        linkedin_url="https://www.linkedin.com/in/arbuzov/"
    )
    
    # Print results
    print("\nExtracted Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    return profile


def example_batch_extraction():
    """Example: Extract multiple profiles from a list using Linkup.so"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Profile Extraction with Linkup.so")
    print("="*60)
    
    if not os.getenv("LINKUP_API_KEY"):
        print("Error: LINKUP_API_KEY environment variable not set!")
        return []
    
    # List of business angels with their LinkedIn URLs
    angels = [
        {
            'name': 'Angel Investor 1',
            'linkedin': 'https://www.linkedin.com/in/angel1'
        },
        {
            'name': 'Angel Investor 2',
            'linkedin': 'https://www.linkedin.com/in/angel2'
        },
        # Add more profiles here
    ]
    
    # Create extractor instance
    extractor = LinkupProfileExtractor(
        depth="standard"  # Use "deep" for more thorough search
    )
    
    # Extract all profiles
    profiles = extractor.extract_profiles_batch(angels)
    
    # Save to files
    extractor.save_profiles_json('extracted_profiles_linkup.json')
    extractor.save_profiles_csv('extracted_profiles_linkup.csv')
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total profiles extracted: {len(profiles)}")
    
    investors = [p for p in profiles if p.get('investment_profile', {}).get('is_investor')]
    print(f"Confirmed investors: {len(investors)}")
    
    return profiles


def example_from_csv_file():
    """Example: Extract profiles from a CSV file using Linkup.so"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extract from CSV File with Linkup.so")
    print("="*60)
    
    if not os.getenv("LINKUP_API_KEY"):
        print("Error: LINKUP_API_KEY environment variable not set!")
        return []
    
    try:
        # Load profiles from CSV file (e.g., estban_members.csv)
        members = LinkupProfileExtractor.load_members_from_csv('estban_members.csv')
        
        # Filter to only those with LinkedIn URLs
        members_with_linkedin = [
            m for m in members 
            if m.get('linkedin')
        ]
        
        print(f"Found {len(members_with_linkedin)} members with LinkedIn profiles")
        
        # Extract profiles (limit to first 3 for demo to save API costs)
        extractor = LinkupProfileExtractor(
            depth="standard"
        )
        profiles = extractor.extract_profiles_batch(members_with_linkedin[:3])
        
        # Save results
        extractor.save_profiles_json('angel_profiles_linkup.json')
        extractor.save_profiles_csv('angel_profiles_linkup.csv')
        
        return profiles
        
    except FileNotFoundError:
        print("estban_members.csv not found. Run the EstBAN scraper first.")
        return []


def example_custom_extraction():
    """Example: Custom extraction with specific parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Extraction with Linkup.so")
    print("="*60)
    
    if not os.getenv("LINKUP_API_KEY"):
        print("Error: LINKUP_API_KEY environment variable not set!")
        return None
    
    extractor = LinkupProfileExtractor(
        depth="deep"  # Use deep search for more thorough results
    )
    
    # Extract single profile
    profile = extractor.extract_profile(
        name="Jane Smith",
        linkedin_url="https://www.linkedin.com/in/janesmith"
    )
    
    # Access specific data
    if profile.get('extraction_status') == 'success':
        personal = profile.get('personal_info', {})
        investment = profile.get('investment_profile', {})
        
        print(f"\nName: {profile.get('name')}")
        print(f"Location: {personal.get('location')}")
        print(f"Current Role: {personal.get('current_role')}")
        print(f"Company: {personal.get('company')}")
        print(f"Is Investor: {investment.get('is_investor')}")
        print(f"Investment Role: {investment.get('investment_role')}")
        print(f"Portfolio Companies: {', '.join(investment.get('portfolio_companies', []))}")
        print(f"Sectors: {', '.join(investment.get('sectors_of_interest', []))}")
        print(f"\nSources Used: {len(profile.get('sources_used', []))} sources")
    
    return profile


def example_direct_api_usage():
    """Example: Direct usage of LinkupClient (matching the provided example)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Direct LinkupClient Usage")
    print("="*60)
    
    if not os.getenv("LINKUP_API_KEY"):
        print("Error: LINKUP_API_KEY environment variable not set!")
        return None
    
    # Try different import patterns
    try:
        from linkup import LinkupClient
    except ImportError:
        try:
            from linkup_sdk import LinkupClient
        except ImportError:
            import linkup
            LinkupClient = linkup.LinkupClient
    
    client = LinkupClient(os.getenv("LINKUP_API_KEY"))
    
    response = client.search(
        query="""You are an expert at extracting business angel and investor profile information from various sources.

Your task is to extract comprehensive profile information about a person based on their name and LinkedIn URL, using web search results and your knowledge.

Extract the following information:

PERSONAL INFORMATION:

- name: Full name

- headline: Professional headline or tagline

- location: Geographic location (city, country, etc.)

- current_role: Current job title

- company: Current company name

- summary: Profile summary or about section (if available)

- experience: List of work experience entries (title, company, duration, description)

- education: List of education entries (school, degree)

- skills: List of skills mentioned

- languages: List of languages spoken

INVESTMENT PROFILE:

- is_investor: Boolean indicating if person is an investor

- investment_role: Specific investment role (e.g., "Angel Investor", "VC Partner", "Venture Partner")

- investment_focus: Investment focus areas (e.g., "Early Stage", "B2B", "SaaS")

- portfolio_companies: List of companies they've invested in or are associated with

- sectors_of_interest: Sectors they invest in (e.g., "fintech", "healthtech", "AI")

- investment_stage: Investment stages (e.g., "seed", "series a", "pre-seed")

- investment_mentions: Any other investment-related information

Use the web search results provided to gather information. If information is not available in search results, you may infer based on context, but clearly indicate uncertainty.

Return the extracted information in the structured format provided.

PERSON TO EXTRACT:

- Name: Mike Arbuzov

- LinkedIn URL: https://www.linkedin.com/in/arbuzov/

Please use web search to find current and accurate information about a person, then extract all available information about their profile, focusing on:

1. Their professional background and experience

2. Their investment activities and portfolio

3. Their areas of interest and expertise

After gathering information through web search, return the extracted data in the structured format matching pydantic schema:

```class ExperienceEntry(BaseModel):

    \"\"\"Work experience entry\"\"\"

    title: Optional[str] = Field(None, description="Job title or role")

    company: Optional[str] = Field(None, description="Company name")

    duration: Optional[str] = Field(None, description="Employment duration")

    description: Optional[str] = Field(None, description="Job description")

class EducationEntry(BaseModel):

    \"\"\"Education entry\"\"\"

    school: Optional[str] = Field(None, description="School or university name")

    degree: Optional[str] = Field(None, description="Degree or field of study")

class PersonalInfo(BaseModel):

    \"\"\"Personal information schema\"\"\"

    name: Optional[str] = Field(None, description="Full name")

    headline: Optional[str] = Field(None, description="Professional headline")

    location: Optional[str] = Field(None, description="Geographic location")

    current_role: Optional[str] = Field(None, description="Current job title")

    company: Optional[str] = Field(None, description="Current company")

    summary: Optional[str] = Field(None, description="Profile summary/about section")

    experience: List[ExperienceEntry] = Field(default_factory=list, description="Work experience entries")

    education: List[EducationEntry] = Field(default_factory=list, description="Education entries")

    skills: List[str] = Field(default_factory=list, description="List of skills")

    languages: List[str] = Field(default_factory=list, description="List of languages")

class InvestmentProfile(BaseModel):

    \"\"\"Investment profile schema\"\"\"

    is_investor: bool = Field(False, description="Whether the person is identified as an investor")

    investment_role: Optional[str] = Field(None, description="Investment role (e.g., Angel Investor, VC Partner)")

    investment_focus: List[str] = Field(default_factory=list, description="Investment focus areas")

    portfolio_companies: List[str] = Field(default_factory=list, description="List of portfolio companies")

    sectors_of_interest: List[str] = Field(default_factory=list, description="Sectors of interest")

    investment_stage: List[str] = Field(default_factory=list, description="Investment stages (e.g., seed, series a)")

    investment_mentions: List[str] = Field(default_factory=list, description="Investment-related mentions")

class ExtractedProfile(BaseModel):

    \"\"\"Complete extracted profile schema\"\"\"

    name: str = Field(..., description="Person's name")

    linkedin_url: str = Field(..., description="LinkedIn profile URL")

    personal_info: PersonalInfo = Field(..., description="Personal information")

    investment_profile: InvestmentProfile = Field(..., description="Investment profile information")

    extraction_status: str = Field("success", description="Extraction status")

    sources_used: List[str] = Field(default_factory=list, description="Sources used for extraction")```""",
        depth="standard",
        output_type="structured",
        structured_output_schema="""{"$schema": "http://json-schema.org/draft-07/schema#","title": "ExtractedProfile","type": "object","description": "Complete extracted profile schema","definitions": {"ExperienceEntry": {"title": "ExperienceEntry","type": "object","description": "Work experience entry","properties": {"title": {"type": ["string", "null"],"description": "Job title or role"},"company": {"type": ["string", "null"],"description": "Company name"},"duration": {"type": ["string", "null"],"description": "Employment duration"},"description": {"type": ["string", "null"],"description": "Job description"}}},"EducationEntry": {"title": "EducationEntry","type": "object","description": "Education entry","properties": {"school": {"type": ["string", "null"],"description": "School or university name"},"degree": {"type": ["string", "null"],"description": "Degree or field of study"}}},"PersonalInfo": {"title": "PersonalInfo","type": "object","description": "Personal information schema","properties": {"name": {"type": ["string", "null"],"description": "Full name"},"headline": {"type": ["string", "null"],"description": "Professional headline"},"location": {"type": ["string", "null"],"description": "Geographic location"},"current_role": {"type": ["string", "null"],"description": "Current job title"},"company": {"type": ["string", "null"],"description": "Current company"},"summary": {"type": ["string", "null"],"description": "Profile summary/about section"},"experience": {"type": "array","description": "Work experience entries","items": {"$ref": "#/definitions/ExperienceEntry"},"default": []},"education": {"type": "array","description": "Education entries","items": {"$ref": "#/definitions/EducationEntry"},"default": []},"skills": {"type": "array","description": "List of skills","items": {"type": "string"},"default": []},"languages": {"type": "array","description": "List of languages","items": {"type": "string"},"default": []}}},"InvestmentProfile": {"title": "InvestmentProfile","type": "object","description": "Investment profile schema","properties": {"is_investor": {"type": "boolean","description": "Whether the person is identified as an investor","default": false},"investment_role": {"type": ["string", "null"],"description": "Investment role (e.g., Angel Investor, VC Partner)"},"investment_focus": {"type": "array","description": "Investment focus areas","items": {"type": "string"},"default": []},"portfolio_companies": {"type": "array","description": "List of portfolio companies","items": {"type": "string"},"default": []},"sectors_of_interest": {"type": "array","description": "Sectors of interest","items": {"type": "string"},"default": []},"investment_stage": {"type": "array","description": "Investment stages (e.g., seed, series a)","items": {"type": "string"},"default": []},"investment_mentions": {"type": "array","description": "Investment-related mentions","items": {"type": "string"},"default": []}}},"properties": {"name": {"type": "string","description": "Person's name"},"linkedin_url": {"type": "string","description": "LinkedIn profile URL"},"personal_info": {"$ref": "#/definitions/PersonalInfo","description": "Personal information"},"investment_profile": {"$ref": "#/definitions/InvestmentProfile","description": "Investment profile information"},"extraction_status": {"type": "string","description": "Extraction status","default": "success"},"sources_used": {"type": "array","description": "Sources used for extraction","items": {"type": "string"},"default": []}},"required": ["name", "linkedin_url", "personal_info", "investment_profile"]}""",
        include_images=False,
        include_sources=False,
    )
    
    print("\nLinkup API Response:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    return response


if __name__ == '__main__':
    # Check for API key
    if not os.getenv("LINKUP_API_KEY"):
        print("="*60)
        print("WARNING: LINKUP_API_KEY not set!")
        print("="*60)
        print("Please set your Linkup API key:")
        print("  export LINKUP_API_KEY='your-api-key-here'")
        print("\nOr pass it directly when creating the extractor:")
        print("  extractor = LinkupProfileExtractor(api_key='your-key')")
        print("="*60)
    
    # Run example
    example_single_profile()

