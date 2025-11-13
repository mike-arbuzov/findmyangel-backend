#!/usr/bin/env python3
"""
LLM-based Profile Extractor for Business Angels
Uses GPT-4 with web search capabilities to extract business angel profiles
based on person name and LinkedIn URL without directly crawling LinkedIn
"""

import os
import json
import csv
import time
from typing import Dict, Optional, List
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from tqdm.auto import tqdm

# Load environment variables from .env file
load_dotenv()


# Define the profile schema using Pydantic
class ExperienceEntry(BaseModel):
    """Work experience entry"""
    title: Optional[str] = Field(None, description="Job title or role")
    company: Optional[str] = Field(None, description="Company name")
    duration: Optional[str] = Field(None, description="Employment duration")
    description: Optional[str] = Field(None, description="Job description")


class EducationEntry(BaseModel):
    """Education entry"""
    school: Optional[str] = Field(None, description="School or university name")
    degree: Optional[str] = Field(None, description="Degree or field of study")


class PersonalInfo(BaseModel):
    """Personal information schema"""
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
    """Investment profile schema"""
    is_investor: bool = Field(False, description="Whether the person is identified as an investor")
    investment_role: Optional[str] = Field(None, description="Investment role (e.g., Angel Investor, VC Partner)")
    investment_focus: List[str] = Field(default_factory=list, description="Investment focus areas")
    portfolio_companies: List[str] = Field(default_factory=list, description="List of portfolio companies")
    sectors_of_interest: List[str] = Field(default_factory=list, description="Sectors of interest")
    investment_stage: List[str] = Field(default_factory=list, description="Investment stages (e.g., seed, series a)")
    investment_mentions: List[str] = Field(default_factory=list, description="Investment-related mentions")


class ExtractedProfile(BaseModel):
    """Complete extracted profile schema"""
    name: str = Field(..., description="Person's name")
    linkedin_url: str = Field(..., description="LinkedIn profile URL")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    personal_info: PersonalInfo = Field(..., description="Personal information")
    investment_profile: InvestmentProfile = Field(..., description="Investment profile information")
    extraction_status: str = Field("success", description="Extraction status")
    sources_used: List[str] = Field(default_factory=list, description="Sources used for extraction")


class LLMProfileExtractor:
    """
    Extracts business angel profiles using GPT-5 with thinking and tooling capabilities via Responses API.
    Does not crawl LinkedIn directly - instead uses web search and LLM reasoning.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-5-mini",
                 use_web_search: bool = True, reasoning_effort: str = "low"):
        """
        Initialize the LLM-based profile extractor
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use (default: "gpt-5")
            use_web_search: Whether to enable web search capabilities (default: True)
            reasoning_effort: Reasoning effort level - "low", "medium", "high", or "max" (default: "medium")
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass openai_api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.use_web_search = use_web_search
        self.reasoning_effort = reasoning_effort
        self.profiles = []
    
    def get_extraction_schema_prompt(self) -> str:
        """Get the prompt that defines the extraction schema"""
        return """You are an expert at extracting business angel and investor profile information from various sources.

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

Return the extracted information in the structured format provided."""
    
    def extract_profile(self, name: str, linkedin_url: str, avatar_url: str = None) -> Dict:
        """
        Extract complete profile data using LLM with web search
        
        Args:
            name: Name of the business angel
            linkedin_url: LinkedIn profile URL
            avatar_url: Optional avatar image URL
            
        Returns:
            Dictionary containing personal and investment profile data
        """
        print(f"\n{'='*60}")
        print(f"Extracting profile for: {name}")
        print(f"LinkedIn URL: {linkedin_url}")
        print(f"{'='*60}")
        
        sources_used = []
        
        # Use Responses API with GPT-5 thinking and tooling capabilities
        print("Using GPT-5 with Responses API, thinking capabilities, and web search...")
        
        extraction_input = [
            {
                "role": "system",
                "content": "You are an expert at extracting structured profile information using web search and reasoning. Use your thinking capabilities to thoroughly analyze information before extracting structured data."
            },
            {
                "role": "user",
                "content": f"""{self.get_extraction_schema_prompt()}

PERSON TO EXTRACT:
- Name: {name}
- LinkedIn URL: {linkedin_url}

Please use web search to find current and accurate information about an EstBAN business angel, then extract all available information about their profile, focusing on:
1. Their professional background and experience
2. Their investment activities and portfolio
3. Their areas of interest and expertise

After gathering information through web search, return the extracted data in the structured format matching the ExtractedProfile schema."""
            }
        ]
        
        # Prepare tools for Responses API
        tools = []
        if self.use_web_search:
            tools.append({"type": "web_search"})
        
        # Normalize reasoning effort to valid values
        reasoning_level = self.reasoning_effort.lower()
        if reasoning_level not in ["low", "medium", "high", "max"]:
            reasoning_level = "low"
        
        # Prepare request parameters for Responses API with parse
        request_params = {
            "model": self.model,
            "input": extraction_input,
            "text_format": ExtractedProfile,
        }
        
        # Add tools if web search is enabled
        if tools:
            request_params["tools"] = tools
        
        # Add text and reasoning parameters for GPT-5
        if "gpt-5" in self.model.lower() or "o1" in self.model.lower():
            request_params["text"] = {
                "verbosity": "low"
            }
            request_params["reasoning"] = {
                "effort": reasoning_level
            }
        
        try:
            # Use Responses API with parse for structured output
            print("Calling Responses API with thinking capabilities and structured output...")
            response = self.client.responses.parse(**request_params)
            
            # Extract parsed profile
            if hasattr(response, 'output_parsed'):
                extracted_profile = response.output_parsed
                
                # Extract sources if available
                if hasattr(response, 'tool_calls'):
                    for tool_call in response.tool_calls:
                        if hasattr(tool_call, 'type') and tool_call.type == 'web_search':
                            sources_used.append(f"Web search: {getattr(tool_call, 'query', '')}")
            else:
                raise Exception("No output_parsed in Responses API response")
                
        except Exception as e:
            print(f"Error using Responses API: {e}")
            return {
                'name': name,
                'linkedin_url': linkedin_url,
                'avatar_url': avatar_url,
                'personal_info': {},
                'investment_profile': {},
                'extraction_status': 'failed',
                'sources_used': [],
                'error': str(e)
            }
        
        # Convert Pydantic model to dict
        profile_dict = extracted_profile.model_dump()
        profile_dict['linkedin_url'] = linkedin_url
        profile_dict['name'] = name
        profile_dict['avatar_url'] = avatar_url
        profile_dict['sources_used'] = sources_used
        
        print("Profile extraction completed successfully!")
        return profile_dict
    
    
    @staticmethod
    def load_members_from_csv(csv_file: str) -> List[Dict]:
        """
        Load members from a CSV file
        
        Args:
            csv_file: Path to CSV file with 'name', 'linkedin', and optionally 'avatar_url' columns
            
        Returns:
            List of dictionaries with 'name', 'linkedin', and 'avatar_url' keys
        """
        members = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    members.append({
                        'name': row.get('name', '').strip(),
                        'linkedin': row.get('linkedin', '').strip(),
                        'avatar_url': row.get('avatar_url', '').strip() or None
                    })
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file}' not found.")
            return []
        except Exception as e:
            print(f"Error loading CSV file '{csv_file}': {e}")
            return []
        
        return members
    
    def extract_profiles_batch(self, profiles: List[Dict],
                               json_filename: str = 'angel_profiles_llm.json',
                               csv_filename: str = 'angel_profiles_llm.csv') -> List[Dict]:
        """
        Extract profiles for multiple business angels
        
        Args:
            profiles: List of dictionaries with 'name' and 'linkedin' keys
            json_filename: Filename for JSON output (default: 'angel_profiles_llm.json')
            csv_filename: Filename for CSV output (default: 'angel_profiles_llm.csv')
            
        Returns:
            List of extracted profile dictionaries
        """
        extracted_profiles = []
        successful_extractions = 0
        
        for i, profile in enumerate(profiles, 1):
            name = profile.get('name', 'Unknown')
            linkedin = profile.get('linkedin') or profile.get('linkedin_url')
            avatar_url = profile.get('avatar_url')
            
            if not linkedin:
                print(f"\nSkipping {name}: No LinkedIn URL provided")
                continue
            
            extracted = self.extract_profile(name, linkedin, avatar_url)
            extracted_profiles.append(extracted)
            successful_extractions += 1
            
            # Update the profiles list for saving
            self.profiles = extracted_profiles
            
            print(f"\nProgress: {i}/{len(profiles)} profiles processed ({successful_extractions} extracted)")
            
            # Save after each successful extraction
            print(f"Saving {len(extracted_profiles)} profiles to files...")
            self.save_profiles_json(json_filename)
            self.save_profiles_csv(csv_filename)
            
            # Add delay between extractions to be respectful
            if i < len(profiles):
                time.sleep(2)
        
        return extracted_profiles
    
    def save_profiles_json(self, filename: str = 'angel_profiles_llm.json'):
        """Save extracted profiles to JSON file"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        # Convert Pydantic models to dicts if needed
        profiles_to_save = []
        for profile in self.profiles:
            if isinstance(profile, dict):
                profiles_to_save.append(profile)
            else:
                profiles_to_save.append(profile.model_dump() if hasattr(profile, 'model_dump') else profile)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profiles_to_save, f, indent=2, ensure_ascii=False)
        print(f"\nProfiles saved to {filename}")
    
    def save_profiles_csv(self, filename: str = 'angel_profiles_llm.csv'):
        """Save extracted profiles to CSV file"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        # Flatten the profile data for CSV
        flattened_profiles = []
        for profile in self.profiles:
            # Handle both dict and Pydantic model
            if hasattr(profile, 'model_dump'):
                profile = profile.model_dump()
            
            personal = profile.get('personal_info', {})
            investment = profile.get('investment_profile', {})
            
            flat_profile = {
                'name': profile.get('name', ''),
                'linkedin_url': profile.get('linkedin_url', ''),
                'avatar_url': profile.get('avatar_url', ''),
                'headline': personal.get('headline', ''),
                'location': personal.get('location', ''),
                'current_role': personal.get('current_role', ''),
                'company': personal.get('company', ''),
                'is_investor': investment.get('is_investor', False),
                'investment_role': investment.get('investment_role', ''),
                'portfolio_companies': '; '.join(investment.get('portfolio_companies', [])),
                'sectors_of_interest': '; '.join(investment.get('sectors_of_interest', [])),
                'investment_stage': '; '.join(investment.get('investment_stage', [])),
                'investment_focus': '; '.join(investment.get('investment_focus', [])),
                'extraction_status': profile.get('extraction_status', ''),
                'sources_used': '; '.join(profile.get('sources_used', []))
            }
            flattened_profiles.append(flat_profile)
        
        fieldnames = [
            'name', 'linkedin_url', 'avatar_url', 'headline', 'location', 'current_role', 'company',
            'is_investor', 'investment_role', 'portfolio_companies', 'sectors_of_interest',
            'investment_stage', 'investment_focus', 'extraction_status', 'sources_used'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_profiles)
        
        print(f"Profiles saved to {filename}")


def extract_angel_profile_llm(name: str, linkedin_url: str, avatar_url: str = None,
                               openai_api_key: Optional[str] = None, model: str = "gpt-5-mini", 
                               reasoning_effort: str = "low") -> Dict:
    """
    Convenience function to extract a single angel profile using LLM with GPT-5 thinking capabilities
    
    Args:
        name: Name of the business angel
        linkedin_url: LinkedIn profile URL
        openai_api_key: OpenAI API key (optional, uses env var if not provided)
        model: OpenAI model to use (default: "gpt-5")
        reasoning_effort: Reasoning effort - "low", "medium", "high", or "max" (default: "medium")
        
    Returns:
        Dictionary containing extracted profile data
    """
    extractor = LLMProfileExtractor(
        openai_api_key=openai_api_key,
        model=model,
        reasoning_effort=reasoning_effort
    )
    return extractor.extract_profile(name, linkedin_url, avatar_url)


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) == 2:
        # Process CSV file with multiple profiles
        member_list_path = sys.argv[1]
        members = LLMProfileExtractor.load_members_from_csv(member_list_path)
        print(f"Loaded {len(members)} members from {member_list_path}")
        
        if not members:
            print("No members found in CSV file. Exiting.")
            sys.exit(1)
        
        # Create extractor and process all profiles
        extractor = LLMProfileExtractor()
        json_filename = 'angel_profiles_llm.json'
        csv_filename = 'angel_profiles_llm.csv'
        
        profiles = extractor.extract_profiles_batch(
            members,
            json_filename=json_filename,
            csv_filename=csv_filename
        )
        
        print(f"\n{'='*60}")
        print(f"EXTRACTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total profiles extracted: {len(profiles)}")
        print(f"Final results saved to {json_filename} and {csv_filename}")
        sys.exit(0)

    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python profile_extractor_llm.py <csv_file>")
        print("  python profile_extractor_llm.py <name> <linkedin_url>")
        print("\nExamples:")
        print("  python profile_extractor_llm.py estban_members.csv")
        print("  python profile_extractor_llm.py 'John Doe' 'https://www.linkedin.com/in/johndoe'")
        sys.exit(1)
    
    name = sys.argv[1]
    linkedin_url = sys.argv[2]
    
    profile = extract_angel_profile_llm(name, linkedin_url)
    print("\n" + "="*60)
    print("EXTRACTED PROFILE:")
    print("="*60)
    print(json.dumps(profile, indent=2, ensure_ascii=False))

