#!/usr/bin/env python3
"""
Profile Extractor for Business Angels
Extracts business angel personal and investment profile data from LinkedIn
based on name and LinkedIn URL
"""

from bs4 import BeautifulSoup
import json
import time
import csv
from urllib.parse import urlparse
from typing import Dict, Optional, List
from playwright.sync_api import sync_playwright, Browser, Page


class ProfileExtractor:
    """
    Extracts business angel personal and investment profile data from LinkedIn
    based on name and LinkedIn URL
    """
    
    # Investment-related keywords to identify investment activities
    INVESTMENT_KEYWORDS = [
        'investor', 'investment', 'angel', 'venture', 'capital', 'vc', 'vc firm',
        'portfolio', 'startup', 'fund', 'equity', 'seed', 'series a', 'series b',
        'series c', 'backing', 'backed', 'invested', 'investing', 'advisory',
        'board member', 'board of directors', 'advisor', 'mentor'
    ]
    
    # Sector keywords
    SECTOR_KEYWORDS = [
        'tech', 'technology', 'saas', 'fintech', 'healthtech', 'edtech',
        'biotech', 'ai', 'artificial intelligence', 'ml', 'machine learning',
        'blockchain', 'crypto', 'e-commerce', 'marketplace', 'b2b', 'b2c',
        'enterprise', 'consumer', 'mobile', 'software', 'hardware', 'iot',
        'robotics', 'automation', 'energy', 'clean tech', 'sustainability'
    ]
    
    def __init__(self, delay=2, headless=False):
        """
        Initialize the profile extractor
        
        Args:
            delay: Delay between requests in seconds (default: 2)
            headless: Whether to run browser in headless mode (default: True)
        """
        self.playwright = sync_playwright().start()
        self.browser: Browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        self.delay = delay
        self.profiles = []
    
    def __del__(self):
        """Cleanup browser resources"""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def close(self):
        """Explicitly close browser and playwright"""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def normalize_linkedin_url(self, url: str) -> str:
        """Normalize LinkedIn URL to standard format"""
        if not url:
            return None
        
        # Remove query parameters and fragments
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Ensure it's a LinkedIn URL
        if 'linkedin.com' not in normalized.lower():
            return None
        
        # Remove trailing slash
        normalized = normalized.rstrip('/')
        
        return normalized
    
    def get_linkedin_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch LinkedIn profile page using Playwright"""
        normalized_url = self.normalize_linkedin_url(url)
        if not normalized_url:
            print(f"Invalid LinkedIn URL: {url}")
            return None
        
        page: Page = None
        try:
            print(f"Fetching LinkedIn profile: {normalized_url}")
            page = self.context.new_page()
            
            # Navigate to the LinkedIn profile
            response = page.goto(normalized_url, wait_until='networkidle', timeout=30000)
            
            if not response:
                print(f"Error: No response received for {normalized_url}")
                return None
            
            # Check if we got redirected to login page
            current_url = page.url.lower()
            if 'login' in current_url or 'authwall' in current_url:
                print(f"Warning: LinkedIn may require authentication for {normalized_url}")
                html_content = page.content()
                with open('page.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Page content saved to page.html")
                return None
            
            # Wait a bit for dynamic content to load
            page.wait_for_timeout(2000)
            
            # Get page content
            html_content = page.content()
            
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            print(f"Error fetching LinkedIn profile {normalized_url}: {e}")
            return None
        finally:
            if page:
                page.close()
    
    def extract_personal_info(self, soup: BeautifulSoup, name: str = None) -> Dict:
        """Extract personal information from LinkedIn profile"""
        personal_info = {
            'name': name,
            'headline': None,
            'location': None,
            'current_role': None,
            'company': None,
            'summary': None,
            'experience': [],
            'education': [],
            'skills': [],
            'languages': []
        }
        
        if not soup:
            return personal_info
        
        # Extract name (if not provided)
        if not personal_info['name']:
            name_elem = soup.find('h1', class_=lambda x: x and ('text-heading' in str(x) or 'top-card' in str(x)))
            if not name_elem:
                name_elem = soup.find('h1')
            if name_elem:
                personal_info['name'] = name_elem.get_text(strip=True)
        
        # Extract headline
        headline_elem = soup.find('div', class_=lambda x: x and ('text-body-medium' in str(x) or 'headline' in str(x).lower()))
        if headline_elem:
            personal_info['headline'] = headline_elem.get_text(strip=True)
        
        # Extract location
        location_elem = soup.find('span', class_=lambda x: x and ('text-body-small' in str(x) or 'location' in str(x).lower()))
        if location_elem:
            location_text = location_elem.get_text(strip=True)
            if location_text and 'connections' not in location_text.lower():
                personal_info['location'] = location_text
        
        # Extract summary/about section
        about_section = soup.find('section', {'id': lambda x: x and 'about' in x.lower()})
        if not about_section:
            about_section = soup.find('div', class_=lambda x: x and ('about' in str(x).lower() or 'summary' in str(x).lower()))
        if about_section:
            summary_text = about_section.get_text(strip=True)
            if len(summary_text) > 50:  # Filter out short/irrelevant text
                personal_info['summary'] = summary_text[:1000]  # Limit length
        
        # Extract experience section
        experience_section = soup.find('section', {'id': lambda x: x and 'experience' in x.lower()})
        if not experience_section:
            experience_section = soup.find('div', class_=lambda x: x and 'experience' in str(x).lower())
        
        if experience_section:
            exp_items = experience_section.find_all(['li', 'div'], class_=lambda x: x and ('experience' in str(x).lower() or 'position' in str(x).lower()))
            for item in exp_items[:10]:  # Limit to 10 most recent
                exp_data = {}
                
                # Extract role/title
                title_elem = item.find(['h3', 'h4', 'span'], class_=lambda x: x and ('title' in str(x).lower() or 'role' in str(x).lower()))
                if title_elem:
                    exp_data['title'] = title_elem.get_text(strip=True)
                
                # Extract company
                company_elem = item.find(['span', 'a'], class_=lambda x: x and ('company' in str(x).lower() or 'organization' in str(x).lower()))
                if company_elem:
                    exp_data['company'] = company_elem.get_text(strip=True)
                
                # Extract duration
                duration_elem = item.find('span', class_=lambda x: x and ('date' in str(x).lower() or 'duration' in str(x).lower()))
                if duration_elem:
                    exp_data['duration'] = duration_elem.get_text(strip=True)
                
                # Extract description
                desc_elem = item.find('div', class_=lambda x: x and ('description' in str(x).lower() or 'details' in str(x).lower()))
                if desc_elem:
                    exp_data['description'] = desc_elem.get_text(strip=True)[:500]
                
                if exp_data.get('title') or exp_data.get('company'):
                    personal_info['experience'].append(exp_data)
        
        # Set current role from first experience entry
        if personal_info['experience']:
            first_exp = personal_info['experience'][0]
            personal_info['current_role'] = first_exp.get('title')
            personal_info['company'] = first_exp.get('company')
        
        # Extract education
        education_section = soup.find('section', {'id': lambda x: x and 'education' in x.lower()})
        if not education_section:
            education_section = soup.find('div', class_=lambda x: x and 'education' in str(x).lower())
        
        if education_section:
            edu_items = education_section.find_all(['li', 'div'], class_=lambda x: x and 'education' in str(x).lower())
            for item in edu_items[:5]:  # Limit to 5
                edu_data = {}
                
                school_elem = item.find(['h3', 'h4', 'span'], class_=lambda x: x and ('school' in str(x).lower() or 'university' in str(x).lower()))
                if school_elem:
                    edu_data['school'] = school_elem.get_text(strip=True)
                
                degree_elem = item.find('span', class_=lambda x: x and ('degree' in str(x).lower() or 'field' in str(x).lower()))
                if degree_elem:
                    edu_data['degree'] = degree_elem.get_text(strip=True)
                
                if edu_data.get('school'):
                    personal_info['education'].append(edu_data)
        
        return personal_info
    
    def extract_investment_profile(self, soup: BeautifulSoup, personal_info: Dict) -> Dict:
        """Extract investment-related information from LinkedIn profile"""
        investment_profile = {
            'is_investor': False,
            'investment_role': None,
            'investment_focus': [],
            'portfolio_companies': [],
            'sectors_of_interest': [],
            'investment_stage': [],
            'investment_mentions': []
        }
        
        if not soup:
            return investment_profile
        
        # Combine all text from the profile for analysis
        all_text = soup.get_text().lower()
        
        # Check if person is an investor based on keywords
        investor_score = sum(1 for keyword in self.INVESTMENT_KEYWORDS if keyword in all_text)
        investment_profile['is_investor'] = investor_score >= 2
        
        # Extract investment role from headline and experience
        headline = personal_info.get('headline', '').lower()
        summary = personal_info.get('summary', '').lower()
        
        for keyword in ['angel investor', 'venture capitalist', 'vc partner', 'investor', 'angel', 'vc']:
            if keyword in headline or keyword in summary:
                investment_profile['investment_role'] = keyword.title()
                investment_profile['is_investor'] = True
                break
        
        # Extract portfolio companies from experience and summary
        portfolio_keywords = ['portfolio', 'invested in', 'backed', 'investment in', 'funding']
        combined_text = f"{headline} {summary} {' '.join([exp.get('description', '') for exp in personal_info.get('experience', [])])}"
        
        # Look for company names mentioned with investment keywords
        for exp in personal_info.get('experience', []):
            company = exp.get('company', '')
            title = exp.get('title', '').lower()
            description = exp.get('description', '').lower()
            
            # Check if role is investment-related
            if any(keyword in title for keyword in self.INVESTMENT_KEYWORDS):
                if company and company not in investment_profile['portfolio_companies']:
                    investment_profile['portfolio_companies'].append(company)
            
            # Check description for investment mentions
            if any(keyword in description for keyword in portfolio_keywords):
                if company:
                    investment_profile['portfolio_companies'].append(company)
        
        # Extract sectors of interest
        for sector in self.SECTOR_KEYWORDS:
            if sector in all_text:
                if sector not in investment_profile['sectors_of_interest']:
                    investment_profile['sectors_of_interest'].append(sector)
        
        # Extract investment stage preferences
        stage_keywords = {
            'pre-seed': ['pre-seed', 'preseed', 'idea stage'],
            'seed': ['seed', 'seed round'],
            'series a': ['series a', 'series-a', 'seriesa'],
            'series b': ['series b', 'series-b', 'seriesb'],
            'series c': ['series c', 'series-c', 'seriesc'],
            'growth': ['growth', 'growth stage', 'late stage']
        }
        
        for stage, keywords in stage_keywords.items():
            if any(kw in all_text for kw in keywords):
                investment_profile['investment_stage'].append(stage)
        
        # Extract investment focus areas
        focus_areas = []
        if 'early stage' in all_text or 'early-stage' in all_text:
            focus_areas.append('Early Stage')
        if 'late stage' in all_text or 'late-stage' in all_text:
            focus_areas.append('Late Stage')
        if 'b2b' in all_text or 'b-to-b' in all_text:
            focus_areas.append('B2B')
        if 'b2c' in all_text or 'b-to-c' in all_text:
            focus_areas.append('B2C')
        
        investment_profile['investment_focus'] = focus_areas
        
        return investment_profile
    
    def extract_profile(self, name: str, linkedin_url: str) -> Dict:
        """
        Extract complete profile data (personal + investment) from LinkedIn
        
        Args:
            name: Name of the business angel
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Dictionary containing personal and investment profile data
        """
        print(f"\n{'='*60}")
        print(f"Extracting profile for: {name}")
        print(f"LinkedIn URL: {linkedin_url}")
        print(f"{'='*60}")
        
        # Fetch LinkedIn page
        soup = self.get_linkedin_page(linkedin_url)
        
        if not soup:
            print(f"Could not fetch LinkedIn profile for {name}")
            return {
                'name': name,
                'linkedin_url': linkedin_url,
                'personal_info': {},
                'investment_profile': {},
                'extraction_status': 'failed'
            }
        
        # Extract personal information
        personal_info = self.extract_personal_info(soup, name)
        
        # Extract investment profile
        investment_profile = self.extract_investment_profile(soup, personal_info)
        
        # Combine into complete profile
        profile = {
            'name': personal_info.get('name') or name,
            'linkedin_url': self.normalize_linkedin_url(linkedin_url),
            'personal_info': personal_info,
            'investment_profile': investment_profile,
            'extraction_status': 'success'
        }
        
        # Be polite - delay between requests
        time.sleep(self.delay)
        
        return profile
    
    @staticmethod
    def load_members_from_csv(csv_file: str) -> List[Dict]:
        """
        Load members from a CSV file
        
        Args:
            csv_file: Path to CSV file with 'name' and 'linkedin' columns
            
        Returns:
            List of dictionaries with 'name' and 'linkedin' keys
        """
        members = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    members.append({
                        'name': row.get('name', '').strip(),
                        'linkedin': row.get('linkedin', '').strip()
                    })
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_file}' not found.")
            return []
        except Exception as e:
            print(f"Error loading CSV file '{csv_file}': {e}")
            return []
        
        return members
    
    def extract_profiles_batch(self, profiles: List[Dict]) -> List[Dict]:
        """
        Extract profiles for multiple business angels
        
        Args:
            profiles: List of dictionaries with 'name' and 'linkedin' keys
            
        Returns:
            List of extracted profile dictionaries
        """
        extracted_profiles = []
        
        for i, profile in enumerate(profiles, 1):
            name = profile.get('name', 'Unknown')
            linkedin = profile.get('linkedin') or profile.get('linkedin_url')
            
            if not linkedin:
                print(f"\nSkipping {name}: No LinkedIn URL provided")
                continue
            
            extracted = self.extract_profile(name, linkedin)
            extracted_profiles.append(extracted)
            
            print(f"\nProgress: {i}/{len(profiles)} profiles extracted")
        
        self.profiles = extracted_profiles
        return extracted_profiles
    
    def save_profiles_json(self, filename: str = 'angel_profiles.json'):
        """Save extracted profiles to JSON file"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        print(f"\nProfiles saved to {filename}")
    
    def save_profiles_csv(self, filename: str = 'angel_profiles.csv'):
        """Save extracted profiles to CSV file"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        # Flatten the profile data for CSV
        flattened_profiles = []
        for profile in self.profiles:
            personal = profile.get('personal_info', {})
            investment = profile.get('investment_profile', {})
            
            flat_profile = {
                'name': profile.get('name', ''),
                'linkedin_url': profile.get('linkedin_url', ''),
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
                'extraction_status': profile.get('extraction_status', '')
            }
            flattened_profiles.append(flat_profile)
        
        fieldnames = [
            'name', 'linkedin_url', 'headline', 'location', 'current_role', 'company',
            'is_investor', 'investment_role', 'portfolio_companies', 'sectors_of_interest',
            'investment_stage', 'investment_focus', 'extraction_status'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_profiles)
        
        print(f"Profiles saved to {filename}")


def extract_angel_profile(name: str, linkedin_url: str) -> Dict:
    """
    Convenience function to extract a single angel profile
    
    Args:
        name: Name of the business angel
        linkedin_url: LinkedIn profile URL
        
    Returns:
        Dictionary containing extracted profile data
    """
    extractor = ProfileExtractor()
    return extractor.extract_profile(name, linkedin_url)

