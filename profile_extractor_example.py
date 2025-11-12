#!/usr/bin/env python3
"""
Example usage of the ProfileExtractor class
Demonstrates how to extract business angel profiles from LinkedIn
"""

from profile_extractor import ProfileExtractor, extract_angel_profile
import json


def example_single_profile():
    """Example: Extract a single profile"""
    print("="*60)
    print("EXAMPLE 1: Extract Single Profile")
    print("="*60)
    
    # Extract profile for a single business angel
    profile = extract_angel_profile(
        name="John Doe",
        linkedin_url="https://www.linkedin.com/in/johndoe"
    )
    
    # Print results
    print("\nExtracted Profile:")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    
    return profile


def example_batch_extraction():
    """Example: Extract multiple profiles from a list"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Batch Profile Extraction")
    print("="*60)
    
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
    extractor = ProfileExtractor(delay=2)  # 2 second delay between requests
    
    # Extract all profiles
    profiles = extractor.extract_profiles_batch(angels)
    
    # Save to files
    extractor.save_profiles_json('extracted_profiles.json')
    extractor.save_profiles_csv('extracted_profiles.csv')
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Total profiles extracted: {len(profiles)}")
    
    investors = [p for p in profiles if p.get('investment_profile', {}).get('is_investor')]
    print(f"Confirmed investors: {len(investors)}")
    
    return profiles


def example_from_csv_file():
    """Example: Extract profiles from a CSV file (e.g., from EstBAN scraper)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Extract from CSV File")
    print("="*60)
    
    try:
        # Load profiles from CSV file (e.g., estban_members.csv)
        members = ProfileExtractor.load_members_from_csv('estban_members.csv')
        
        # Filter to only those with LinkedIn URLs
        members_with_linkedin = [
            m for m in members 
            if m.get('linkedin')
        ]
        
        print(f"Found {len(members_with_linkedin)} members with LinkedIn profiles")
        
        # Extract profiles (limit to first 5 for demo)
        extractor = ProfileExtractor(delay=2)
        profiles = extractor.extract_profiles_batch(members_with_linkedin[:5])
        
        # Save results
        extractor.save_profiles_json('angel_profiles.json')
        extractor.save_profiles_csv('angel_profiles.csv')
        
        return profiles
        
    except FileNotFoundError:
        print("estban_members.csv not found. Run the EstBAN scraper first.")
        return []


def example_custom_extraction():
    """Example: Custom extraction with specific parameters"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Extraction")
    print("="*60)
    
    extractor = ProfileExtractor(delay=3)  # Longer delay for rate limiting
    
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
    
    return profile


if __name__ == '__main__':
    example_from_csv_file()
