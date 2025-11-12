#!/usr/bin/env python3
"""
Example usage of the LLMProfileExtractor class
Demonstrates how to extract business angel profiles using GPT-4 with web search
"""

from profile_extractor_llm import LLMProfileExtractor, extract_angel_profile_llm
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def example_single_profile():
    """Example: Extract a single profile using LLM"""
    print("="*60)
    print("EXAMPLE 1: Extract Single Profile with LLM")
    print("="*60)
    
    # Make sure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        return None
    
    # Extract profile for a single business angel
    profile = extract_angel_profile_llm(
        name="Mike Arbuzov",
        linkedin_url="https://www.linkedin.com/in/arbuzov"
    )
    
    # Print results
    print("\nExtracted Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    return profile


def example_batch_extraction():
    """Example: Extract multiple profiles from a list using LLM"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Profile Extraction with LLM")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
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
    extractor = LLMProfileExtractor(
        model="gpt-4o",  # Use GPT-4o for best results
        use_web_search=True  # Enable web search
    )
    
    # Extract all profiles
    profiles = extractor.extract_profiles_batch(angels)
    
    # Save to files
    extractor.save_profiles_json('extracted_profiles_llm.json')
    extractor.save_profiles_csv('extracted_profiles_llm.csv')
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total profiles extracted: {len(profiles)}")
    
    investors = [p for p in profiles if p.get('investment_profile', {}).get('is_investor')]
    print(f"Confirmed investors: {len(investors)}")
    
    return profiles


def example_from_csv_file():
    """Example: Extract profiles from a CSV file using LLM"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extract from CSV File with LLM")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        return []
    
    try:
        # Load profiles from CSV file (e.g., estban_members.csv)
        members = LLMProfileExtractor.load_members_from_csv('estban_members.csv')
        
        # Filter to only those with LinkedIn URLs
        members_with_linkedin = [
            m for m in members 
            if m.get('linkedin')
        ]
        
        print(f"Found {len(members_with_linkedin)} members with LinkedIn profiles")
        
        # Extract profiles (limit to first 3 for demo to save API costs)
        extractor = LLMProfileExtractor(
            model="gpt-4o",
            use_web_search=True
        )
        profiles = extractor.extract_profiles_batch(members_with_linkedin[:3])
        
        # Save results
        extractor.save_profiles_json('angel_profiles_llm.json')
        extractor.save_profiles_csv('angel_profiles_llm.csv')
        
        return profiles
        
    except FileNotFoundError:
        print("estban_members.csv not found. Run the EstBAN scraper first.")
        return []


def example_custom_extraction():
    """Example: Custom extraction with specific parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Extraction with LLM")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        return None
    
    extractor = LLMProfileExtractor(
        model="gpt-4o",  # Use GPT-4o
        use_web_search=True  # Enable web search
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


def example_without_web_search():
    """Example: Extract profile without web search (LLM only)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Extraction without Web Search")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set!")
        return None
    
    extractor = LLMProfileExtractor(
        model="gpt-4o",
        use_web_search=False  # Disable web search, rely only on LLM knowledge
    )
    
    profile = extractor.extract_profile(
        name="Elon Musk",
        linkedin_url="https://www.linkedin.com/in/elonmusk"
    )
    
    print("\nExtracted Profile (LLM only, no web search):")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    return profile


if __name__ == '__main__':
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("="*60)
        print("WARNING: OPENAI_API_KEY not set!")
        print("="*60)
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr pass it directly when creating the extractor:")
        print("  extractor = LLMProfileExtractor(openai_api_key='your-key')")
        print("="*60)
    
    # Run example
    example_single_profile()

