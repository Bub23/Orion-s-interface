import requests
import json

class WebhookIntegration:
    """Custom webhook/API integration for Orion."""
    
    def __init__(self):
        self.webhooks = {}
        self.integrations = {}
    
    def register_webhook(self, name, url, method="POST", headers=None):
        """Register a webhook endpoint."""
        self.webhooks[name] = {
            "url": url,
            "method": method,
            "headers": headers or {}
        }
        return {"success": True, "webhook": name}
    
    def trigger_webhook(self, name, data):
        """Trigger a webhook."""
        if name not in self.webhooks:
            return {"success": False, "error": "Webhook not found"}
        
        webhook = self.webhooks[name]
        
        try:
            if webhook["method"].upper() == "POST":
                response = requests.post(
                    webhook["url"],
                    json=data,
                    headers=webhook["headers"],
                    timeout=10
                )
            elif webhook["method"].upper() == "GET":
                response = requests.get(
                    webhook["url"],
                    params=data,
                    headers=webhook["headers"],
                    timeout=10
                )
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.text[:500]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def register_integration(self, name, config):
        """Register a custom integration."""
        self.integrations[name] = config
        return {"success": True, "integration": name}
    
    def call_integration(self, name, action, params=None):
        """Call a custom integration."""
        if name not in self.integrations:
            return {"success": False, "error": "Integration not found"}
        
        integration = self.integrations[name]
        
        try:
            # Make HTTP request to integration endpoint
            url = f"{integration['base_url']}/{action}"
            
            response = requests.post(
                url,
                json=params or {},
                headers=integration.get('headers', {}),
                timeout=10
            )
            
            return {
                "success": True,
                "data": response.json() if response.headers.get('content-type') == 'application/json' else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_webhooks(self):
        """Get all registered webhooks."""
        return list(self.webhooks.keys())
    
    def get_all_integrations(self):
        """Get all registered integrations."""
        return list(self.integrations.keys())
