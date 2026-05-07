class BrowsingCoordinator:
    """Coordinate browsing requests and data extraction."""
    
    def __init__(self, browser_automation):
        self.browser = browser_automation
        self.browsing_history = []
    
    def handle_browse_request(self, request):
        """Process a browse request from user."""
        request_lower = request.lower()
        
        # Detect request type
        if "search" in request_lower or "find" in request_lower:
            return self.handle_search(request)
        elif "go to" in request_lower or "visit" in request_lower:
            return self.handle_visit(request)
        elif "extract" in request_lower or "get data" in request_lower:
            return self.handle_extract(request)
        else:
            return self.handle_generic_browse(request)
    
    def handle_search(self, query):
        """Search for information."""
        # Extract search term
        search_term = query.replace("search", "").replace("find", "").strip()
        
        results = self.browser.search_google(search_term)
        
        summary = f"Found {len(results)} results for '{search_term}':\n\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            if result['snippet']:
                summary += f"   {result['snippet'][:150]}...\n"
            summary += f"   {result['url']}\n\n"
        
        # Log to history
        self.browsing_history.append({
            "type": "search",
            "query": search_term,
            "results_count": len(results),
            "timestamp": str(__import__('datetime').datetime.now())
        })
        
        return summary
    
    def handle_visit(self, request):
        """Visit a website."""
        # Extract URL
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', request)
        
        if urls:
            url = urls[0]
        else:
            # Try to construct from text
            domain = request.replace("go to", "").replace("visit", "").strip()
            url = f"https://{domain}" if not domain.startswith('http') else domain
        
        success = self.browser.navigate(url)
        
        if success:
            content = self.browser.get_page_content()
            links = self.browser.get_links()
            
            summary = f"✓ Successfully visited: {url}\n\n"
            summary += f"Page summary:\n{content[:500]}...\n\n"
            summary += f"Found {len(links)} links on page"
            
            self.browsing_history.append({
                "type": "visit",
                "url": url,
                "timestamp": str(__import__('datetime').datetime.now())
            })
            
            return summary
        else:
            return f"✗ Failed to visit {url}"
    
    def handle_extract(self, request):
        """Extract data from current page."""
        tables = self.browser.extract_data_table()
        content = self.browser.get_page_content()
        
        summary = "Extracted data:\n\n"
        
        if tables:
            summary += f"Found {len(tables)} table(s):\n"
            for i, table in enumerate(tables, 1):
                summary += f"\nTable {i}:\n"
                for row in table[:5]:  # First 5 rows
                    summary += " | ".join(row[:4]) + "\n"  # First 4 cols
        
        if content:
            summary += f"\n\nPage content excerpt:\n{content[:300]}..."
        
        return summary
    
    def handle_generic_browse(self, request):
        """Generic browse handling."""
        # Try to extract a domain or URL from request
        import re
        
        # Look for domain patterns
        domains = re.findall(r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b', request.lower())
        
        if domains:
            url = f"https://{domains[0]}"
            success = self.browser.navigate(url)
            
            if success:
                content = self.browser.get_page_content()
                return f"Browsed {url}\n\nContent:\n{content[:500]}..."
        
        return "Could not determine what to browse. Try: 'search for X' or 'visit website.com'"
    
    def get_history(self):
        """Get browsing history."""
        return self.browsing_history
