"""
Subprocess manager for Node.js Mermaid validator.

Handles lifecycle management, health monitoring, and automatic recovery
of the Node.js validation server subprocess.
"""
import logging
import httpx



logger = logging.getLogger(__name__)


class MermaidSubprocessManager:
    def __init__(self, base_url: str = "http://localhost:51234"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.sync_client = httpx.Client(timeout=30.0)
    
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
        Validate Mermaid diagram code (async).

        Args:
            mermaid_code: Mermaid diagram code to validate

        Returns:
            Validation result dictionary

        Raises:
            httpx.HTTPError: If validation request fails
        """
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

    def validate_sync(self, mermaid_code: str) -> dict:
        """
        Validate Mermaid diagram code (synchronous).

        Args:
            mermaid_code: Mermaid diagram code to validate

        Returns:
            Validation result dictionary

        Raises:
            httpx.HTTPError: If validation request fails
        """
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
    
    async def close(self):
        """Close HTTP clients"""
        await self.client.aclose()
        self.sync_client.close()