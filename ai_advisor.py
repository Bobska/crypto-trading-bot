"""
AI Advisor Module
Provides AI-powered trading insights and recommendations
"""
import requests
from logger_setup import setup_logger
from typing import Optional

class AIAdvisor:
    """
    AI Advisor for Trading Insights
    
    Connects to AI service to provide market analysis and trading recommendations.
    Includes health checking and graceful degradation when AI service is unavailable.
    """
    
    def __init__(self, api_url: str = 'http://localhost:8000'):
        """
        Initialize AI Advisor with health checking
        
        Args:
            api_url: URL of the AI service API (default: 'http://localhost:8000')
        """
        self.logger = setup_logger('AIAdvisor')
        self.api_url = api_url.rstrip('/')  # Remove trailing slash
        self.enabled = True
        
        # Test connection to AI API
        self._health_check()
        
        if self.enabled:
            self.logger.info(f"AI Advisor initialized with API: {self.api_url}")
        else:
            self.logger.info(f"AI Advisor initialized in fallback mode (API unavailable)")
    
    def _health_check(self) -> None:
        """
        Check if AI API is available and responding
        Sets enabled flag based on health check result
        """
        try:
            health_url = f"{self.api_url}/health"
            
            self.logger.debug(f"Testing AI API health at: {health_url}")
            
            # Make health check request with short timeout
            response = requests.get(health_url, timeout=2)
            
            if response.status_code == 200:
                self.logger.info(f"✅ AI API health check successful - Status: {response.status_code}")
                self.enabled = True
            else:
                self.logger.warning(f"⚠️ AI API health check failed - Status: {response.status_code}")
                self.enabled = False
                
        except requests.exceptions.Timeout:
            self.logger.warning(f"⚠️ AI API health check timeout - API may be slow or unavailable")
            self.enabled = False
            
        except requests.exceptions.ConnectionError:
            self.logger.warning(f"⚠️ AI API connection failed - Service may be offline")
            self.enabled = False
            
        except Exception as e:
            self.logger.warning(f"⚠️ AI API health check error: {str(e)}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """
        Check if AI advisor is enabled and available
        
        Returns:
            bool: True if AI service is available, False otherwise
        """
        return self.enabled
    
    def get_status(self) -> dict:
        """
        Get current AI advisor status
        
        Returns:
            Dictionary with advisor status information
        """
        return {
            'enabled': self.enabled,
            'api_url': self.api_url,
            'service_status': 'online' if self.enabled else 'offline'
        }