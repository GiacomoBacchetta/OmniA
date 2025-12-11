import re
import httpx
from typing import Dict, Optional, Tuple
from config import settings


class LocationService:
    """Service for extracting and geocoding location information"""
    
    def __init__(self):
        self.nominatim_client = httpx.AsyncClient(
            base_url="https://nominatim.openstreetmap.org",
            headers={"User-Agent": "OmniA/1.0"}
        )
    
    async def extract_location_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract location information from text
        
        Supports:
        - Google Maps URLs
        - Coordinates (lat, lon)
        - Addresses (Via, Street, etc.)
        """
        # Try to extract Google Maps URL
        google_maps_url = self._extract_google_maps_url(text)
        
        if google_maps_url:
            # Extract coordinates from Google Maps URL
            coords = self._extract_coords_from_maps_url(google_maps_url)
            if coords:
                lat, lon = coords
                # Try to get address from coordinates
                address = await self.reverse_geocode(lat, lon)
                return {
                    "google_maps_url": google_maps_url,
                    "latitude": lat,
                    "longitude": lon,
                    "address": address
                }
        
        # Try to extract coordinates directly (e.g., "45.4642, 9.1900")
        coords = self._extract_coordinates(text)
        if coords:
            lat, lon = coords
            address = await self.reverse_geocode(lat, lon)
            return {
                "latitude": lat,
                "longitude": lon,
                "address": address
            }
        
        # Try to extract address (Via, Street, etc.)
        address = self._extract_address(text)
        if address:
            # Geocode address to get coordinates
            location = await self.geocode(address)
            if location:
                return location
        
        return None
    
    def _extract_google_maps_url(self, text: str) -> Optional[str]:
        """Extract Google Maps URL from text"""
        patterns = [
            r'https?://(?:www\.)?google\.com/maps[^\s<>"]+',
            r'https?://maps\.google\.com[^\s<>"]+',
            r'https?://goo\.gl/maps/[^\s<>"]+',
            r'https?://maps\.app\.goo\.gl/[^\s<>"]+',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_coords_from_maps_url(self, url: str) -> Optional[Tuple[float, float]]:
        """Extract latitude and longitude from Google Maps URL"""
        # Pattern: @lat,lon or q=lat,lon
        patterns = [
            r'@(-?\d+\.\d+),(-?\d+\.\d+)',
            r'q=(-?\d+\.\d+),(-?\d+\.\d+)',
            r'll=(-?\d+\.\d+),(-?\d+\.\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                lat, lon = float(match.group(1)), float(match.group(2))
                return lat, lon
        
        return None
    
    def _extract_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract latitude, longitude coordinates from text"""
        # Pattern: "45.4642, 9.1900" or "45.4642,9.1900"
        pattern = r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)'
        match = re.search(pattern, text)
        
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            # Validate reasonable coordinate ranges
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return lat, lon
        
        return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address from text (Italian-focused but generic)"""
        # Look for common address patterns
        patterns = [
            r'(?:Via|Viale|Corso|Piazza|Strada|Vicolo|Largo)\s+[A-Za-zÀ-ÿ\s]+\d*',
            r'\d+\s+[A-Za-zÀ-ÿ\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return None
    
    async def geocode(self, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates using OpenStreetMap Nominatim
        """
        try:
            response = await self.nominatim_client.get(
                "/search",
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1
                }
            )
            
            if response.status_code == 200:
                results = response.json()
                if results:
                    result = results[0]
                    return {
                        "address": result.get("display_name"),
                        "latitude": float(result["lat"]),
                        "longitude": float(result["lon"]),
                        "place_id": result.get("place_id")
                    }
        
        except Exception as e:
            print(f"Geocoding failed for '{address}': {e}")
        
        return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to address using OpenStreetMap Nominatim
        """
        try:
            response = await self.nominatim_client.get(
                "/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("display_name")
        
        except Exception as e:
            print(f"Reverse geocoding failed for {latitude},{longitude}: {e}")
        
        return None
    
    async def close(self):
        """Close HTTP client"""
        await self.nominatim_client.aclose()
