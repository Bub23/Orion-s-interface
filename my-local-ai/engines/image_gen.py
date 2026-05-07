import os
import requests
from datetime import datetime

class ImageGenerator:
    """Generate images using free APIs."""
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), '../data/generated_images')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_image(self, prompt):
        """Generate image from text prompt using Pollinations.ai (free)."""
        try:
            # Pollinations.ai provides free image generation
            url = "https://image.pollinations.ai/prompt/" + prompt.replace(" ", "%20")
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "prompt": prompt,
                    "filename": filename,
                    "path": filepath,
                    "timestamp": timestamp
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "prompt": prompt
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    def get_generated_images(self):
        """List all generated images."""
        images = []
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                if f.endswith('.png'):
                    images.append({
                        "filename": f,
                        "path": os.path.join(self.output_dir, f)
                    })
        return sorted(images, reverse=True)
