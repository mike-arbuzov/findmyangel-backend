#!/usr/bin/env python3
"""
Scraper for EstBAN members page
Extracts member names and LinkedIn profiles across all paginations
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs


class EstBANScraper:
    def __init__(self, base_url="https://estban.ee/team-and-board/members/"):
        self.base_url = base_url
        self.ajax_url = "https://estban.ee/wp-admin/admin-ajax.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8,ru;q=0.7,et;q=0.6',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://estban.ee',
            'Referer': 'https://estban.ee/team-and-board/members/',
            'X-Requested-With': 'XMLHttpRequest',
        })
        # Set cookie for consent
        self.session.cookies.set('cookieyes-consent', 
            'consentid:d2VMZXNPMGRGaE1WeE90bEpBZHZaeDdEd2dnNlVQSGc,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes')
        self.members = []
        self.base_form_data = None
        self.max_pages = None
    
    def get_page(self, url):
        """Fetch a page and return BeautifulSoup object"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_base_form_data(self, soup):
        """Extract base form data from the first page"""
        # Base form data structure from the curl command
        base_data = {
            'action': 'jet_smart_filters',
            'provider': 'jet-engine/members',
            'defaults[post_status][]': 'publish',
            'defaults[post_type]': 'members',
            'defaults[posts_per_page]': '25',
            'defaults[ignore_sticky_posts]': '1',
            'defaults[order]': 'ASC',
            'defaults[orderby]': 'title',
            'settings[lisitng_id]': '1649',
            'settings[columns]': '1',
            'settings[columns_tablet]': '',
            'settings[columns_mobile]': '',
            'settings[column_min_width]': '240',
            'settings[column_min_width_tablet]': '',
            'settings[column_min_width_mobile]': '',
            'settings[inline_columns_css]': 'false',
            'settings[post_status][]': 'publish',
            'settings[use_random_posts_num]': '',
            'settings[posts_num]': '25',
            'settings[max_posts_num]': '9',
            'settings[not_found_message]': 'No data was found',
            'settings[is_masonry]': '',
            'settings[equal_columns_height]': '',
            'settings[use_load_more]': '',
            'settings[load_more_id]': '',
            'settings[load_more_type]': 'click',
            'settings[load_more_offset][unit]': 'px',
            'settings[load_more_offset][size]': '0',
            'settings[loader_text]': '',
            'settings[loader_spinner]': '',
            'settings[use_custom_post_types]': '',
            'settings[custom_post_types]': '',
            'settings[hide_widget_if]': '',
            'settings[carousel_enabled]': '',
            'settings[slides_to_scroll]': '1',
            'settings[arrows]': 'true',
            'settings[arrow_icon]': 'fa fa-angle-left',
            'settings[dots]': '',
            'settings[autoplay]': 'true',
            'settings[pause_on_hover]': 'true',
            'settings[autoplay_speed]': '5000',
            'settings[infinite]': 'true',
            'settings[center_mode]': '',
            'settings[effect]': 'slide',
            'settings[speed]': '500',
            'settings[inject_alternative_items]': '',
            'settings[scroll_slider_enabled]': '',
            'settings[scroll_slider_on][]': ['desktop', 'tablet', 'mobile'],
            'settings[custom_query]': '',
            'settings[custom_query_id]': '',
            'settings[_element_id]': 'members',
        }
        
        # Try to extract max_num_pages from the first page if available
        # Look for pagination info in script tags or data attributes
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'max_num_pages' in script.string:
                try:
                    # Try to extract max_num_pages value
                    match = re.search(r'max_num_pages["\']?\s*[:=]\s*(\d+)', script.string)
                    if match:
                        self.max_pages = int(match.group(1))
                        print(f"Found max pages: {self.max_pages}")
                except:
                    pass
        
        return base_data
    
    def get_page_via_post(self, page_num):
        """Fetch a page via POST request and return BeautifulSoup object"""
        if not self.base_form_data:
            # Need to get base form data first
            soup = self.get_page(self.base_url)
            if soup:
                self.base_form_data = self.get_base_form_data(soup)
            else:
                return None
        
        # Prepare form data for this page
        form_data = self.base_form_data.copy()
        form_data['defaults[paged]'] = str(page_num)
        form_data['paged'] = str(page_num)
        
        # Add props parameters (these might be needed for pagination)
        # props[page] seems to be the previous page number
        form_data['props[page]'] = str(page_num - 1) if page_num > 1 else '1'
        
        # Build post data as list of tuples to handle array parameters correctly
        post_data = []
        for key, value in form_data.items():
            if isinstance(value, list):
                # For array parameters, add each value separately
                for v in value:
                    post_data.append((key, v))
            else:
                post_data.append((key, value))
        
        try:
            response = self.session.post(self.ajax_url, data=post_data, timeout=10)
            response.raise_for_status()
            
            # The response might be JSON with HTML content
            try:
                json_response = response.json()
                # If it's JSON, extract the HTML content
                if isinstance(json_response, dict):
                    # Try common keys that might contain HTML
                    html_content = None
                    for key in ['content', 'data', 'html', 'result']:
                        if key in json_response:
                            html_content = json_response[key]
                            break
                    
                    if html_content is None:
                        # If no standard key, try to find HTML-like content
                        html_content = str(json_response)
                elif isinstance(json_response, str):
                    html_content = json_response
                else:
                    html_content = str(json_response)
            except (ValueError, json.JSONDecodeError):
                # Response is already HTML
                html_content = response.text
            
            return BeautifulSoup(html_content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page {page_num} via POST: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response content: {e.response.text[:500]}")
            return None
    
    def extract_members_from_page(self, soup):
        """Extract member names and LinkedIn URLs from a page"""
        members = []
        
        # Find all member items
        member_items = soup.find_all('div', class_='jet-listing-grid__item')
        print("Found", len(member_items), "member items")
        
        for item in member_items:
            member_data = {'name': None, 'linkedin': None}
            
            # Extract name
            name_div = item.find('div', class_='jet-listing-dynamic-field__content')
            if name_div:
                member_data['name'] = name_div.get_text(strip=True)
            
            # Extract LinkedIn URL
            # Look for links containing 'linkedin.com' within the member item
            links = item.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if 'linkedin.com' in href.lower():
                    member_data['linkedin'] = href
                    break
            
            # Only add if we have at least a name
            if member_data['name']:
                members.append(member_data)
                print("    ", member_data)
        
        return members
    
    def has_more_pages(self, page_num, soup):
        """Check if there are more pages available"""
        # If we know max_pages, use that
        if self.max_pages:
            return page_num < self.max_pages
        
        # Otherwise, check if we found any members on this page
        # If we found members, there might be more pages
        # We'll also check for pagination indicators in the HTML
        if soup:
            # Check for "Next" button or pagination indicators
            next_links = soup.find_all('a', string=lambda text: text and ('Next' in text or '→' in text))
            if next_links:
                return True
            
            # Check if we found members (if no members, probably no more pages)
            member_items = soup.find_all('div', class_='jet-listing-grid__item')
            if len(member_items) == 0:
                return False
        
        # Default: try next page if we found members on current page
        return True
    
    def scrape_all(self):
        """Scrape all pages using POST requests"""
        page_num = 1
        
        print(f"Starting scrape of {self.base_url}")
        
        # First, get the initial page to extract base form data
        print("Fetching initial page to get form data...")
        initial_soup = self.get_page(self.base_url)
        if not initial_soup:
            print("Failed to fetch initial page, stopping.")
            return []
        
        # Extract base form data and members from first page
        self.base_form_data = self.get_base_form_data(initial_soup)
        page_members = self.extract_members_from_page(initial_soup)
        self.members.extend(page_members)
        print(f"  Found {len(page_members)} members on page 1")
        
        # Continue with POST requests for subsequent pages
        page_num = 2
        
        while True:
            print(f"Scraping page {page_num} via POST...")
            soup = self.get_page_via_post(page_num)
            
            if not soup:
                print(f"Failed to fetch page {page_num}, stopping.")
                break
            
            # Extract members from current page
            page_members = self.extract_members_from_page(soup)
            
            # If no members found, we've reached the end
            if len(page_members) == 0:
                print(f"  No members found on page {page_num}, reached end of pagination.")
                break
            
            self.members.extend(page_members)
            print(f"  Found {len(page_members)} members on page {page_num}")
            
            # Check if there are more pages
            if not self.has_more_pages(page_num, soup):
                print(f"  No more pages available.")
                break
            
            page_num += 1
            time.sleep(1)  # Be polite, wait 1 second between requests
        
        print(f"\nScraping complete! Total members found: {len(self.members)}")
        return self.members
    
    def save_to_json(self, filename='estban_members.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.members, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, filename='estban_members.csv'):
        """Save scraped data to CSV file"""
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'linkedin'])
            writer.writeheader()
            writer.writerows(self.members)
        print(f"Data saved to {filename}")


def main():
    scraper = EstBANScraper()
    members = scraper.scrape_all()
    
    if members:
        scraper.save_to_json()
        scraper.save_to_csv()
        
        # Print summary
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Total members: {len(members)}")
        members_with_linkedin = sum(1 for m in members if m['linkedin'])
        print(f"Members with LinkedIn: {members_with_linkedin}")
        print(f"Members without LinkedIn: {len(members) - members_with_linkedin}")
        print("\nFirst 5 members:")
        for i, member in enumerate(members[:5], 1):
            print(f"  {i}. {member['name']} - {member['linkedin'] or 'No LinkedIn'}")
    else:
        print("No members found!")


if __name__ == '__main__':
    main()

