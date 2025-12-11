import instaloader
from typing import Dict, Optional
from config import settings


class InstagramService:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        # Load session if exists
        # In production, implement proper session management
    
    async def fetch_content(self, url: str) -> Dict:
        """
        Fetch Instagram post/reel content
        
        Returns:
            Dict with caption, media_url, and metadata
        """
        try:
            # Extract shortcode from URL
            # Example: https://www.instagram.com/p/ABC123/ -> ABC123
            shortcode = url.rstrip('/').split('/')[-1]
            
            # Get post
            post = instaloader.Post.from_shortcode(
                self.loader.context,
                shortcode
            )
            
            # Extract data
            return {
                "caption": post.caption or "",
                "media_url": post.url if post.is_video else post.url,
                "metadata": {
                    "likes": post.likes,
                    "comments": post.comments,
                    "date": post.date_utc.isoformat(),
                    "owner": post.owner_username,
                    "is_video": post.is_video,
                    "shortcode": shortcode
                }
            }
        
        except Exception as e:
            # In production, implement proper error handling
            return {
                "caption": f"Failed to fetch Instagram content: {e}",
                "media_url": None,
                "metadata": {
                    "error": str(e),
                    "url": url
                }
            }
