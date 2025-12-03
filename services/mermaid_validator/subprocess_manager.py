"""
Subprocess manager for Node.js Mermaid validator.

Handles lifecycle management, health monitoring, and automatic recovery
of the Node.js validation server subprocess.
"""
import asyncio
import logging
import time
from typing import Optional
import httpx


logger = logging.getLogger(__name__)


class MermaidSubprocessManager:
    def __init__(self, base_url: str = "http://localhost:51234", max_retries: int = 3):
        self.base_url = base_url
        self.max_retries = max_retries
        # Optimized timeout: 30s is sufficient for most validations (8-15s typical)
        # Keep-alive connections for better performance
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.sync_client = httpx.Client(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def _retry_with_backoff(self, operation, *args, **kwargs):
        """
        Execute operation with exponential backoff retry logic.
        
        Args:
            operation: Async function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result from successful operation
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Validator connection failed (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Validator connection failed after {self.max_retries} attempts: {e}")
        
        raise last_exception
    
    def _retry_with_backoff_sync(self, operation, *args, **kwargs):
        """
        Execute operation with exponential backoff retry logic (synchronous).
        
        Args:
            operation: Function to execute
            *args, **kwargs: Arguments to pass to operation
            
        Returns:
            Result from successful operation
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Validator connection failed (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {wait_time}s... Error: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Validator connection failed after {self.max_retries} attempts: {e}")
        
        raise last_exception
    
    async def health_check(self) -> bool:
        """
        Check if validator service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get(f'{self.base_url}/health')
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Validator health check failed: {e}")
            return False

    async def validate(self, mermaid_code: str) -> bool:
        """
        Validate Mermaid diagram code with automatic retry.

        Args:
            mermaid_code: Mermaid diagram code to validate

        Returns:
            Validation result dictionary

        Raises:
            httpx.HTTPError: If validation request fails after all retries
        """
        async def _validate_request():
            try:
                response = await self.client.post(
                    f"{self.base_url}/validate",
                    json={"code": mermaid_code}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Validation request failed: {e}")
                raise
            except Exception as e:
                logger.error(f"An unexpected exception occured when calling validate from MermaidSubprocessManager: {e}")
                raise
        
        return await self._retry_with_backoff(_validate_request)

    def validate_sync(self, mermaid_code: str) -> dict:
        """Validate Mermaid diagram code with automatic retry (synchronous).

        Args:
            mermaid_code: Mermaid diagram code to validate

        Returns:
            Validation result dictionary

        Raises:
            httpx.HTTPError: If validation request fails after all retries
        """
        def _validate_request():
            try:
                response = self.sync_client.post(
                    f"{self.base_url}/validate",
                    json={"code": mermaid_code}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Validation request failed: {e}")
                raise
            except Exception as e:
                logger.error(f"An unexpected exception occured when calling validate_sync from MermaidSubprocessManager: {e}")
                raise
        
        return self._retry_with_backoff_sync(_validate_request)
    
    async def close(self):
        """Close HTTP clients"""
        await self.client.aclose()
        self.sync_client.close()