"""
LLM Client Module

Manages communication with Language Model APIs (OpenAI, HuggingFace, etc.)
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """
    Client for interacting with Language Models.
    
    Supports multiple providers:
    - OpenAI (GPT-3.5, GPT-4)
    - DeepSeek (DeepSeek-Chat, DeepSeek-Coder)
    - HuggingFace (future)
    - Local models (future)
    """
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        timeout: int = 30
    ):
        """
        Initialize the LLM client.
        
        Args:
            provider: LLM provider name ("openai", "deepseek", "huggingface", "local")
            model: Model name (defaults from env if not specified)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            timeout: API request timeout in seconds
        """
        self.provider = provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        if self.provider == "openai":
            self._init_openai(model)
        elif self.provider == "deepseek":
            self._init_deepseek(model)
        else:
            raise NotImplementedError(f"Provider '{provider}' not yet implemented")
    
    def _init_openai(self, model: Optional[str]):
        """Initialize OpenAI client."""
        if OpenAI is None:
            raise ImportError(
                "OpenAI package not installed. Run: pip install openai"
            )
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in .env file or export it."
            )
        
        self.client = OpenAI(api_key=api_key, timeout=self.timeout)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def _init_deepseek(self, model: Optional[str]):
        """Initialize DeepSeek client (uses OpenAI-compatible API)."""
        if OpenAI is None:
            raise ImportError(
                "OpenAI package not installed. Run: pip install openai"
            )
        
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not found in environment variables. "
                "Please set it in .env file or export it."
            )
        
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self.timeout
        )
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    def generate_config(
        self,
        user_prompt: str,
        system_prompt_path: Optional[str] = None
    ) -> Dict:
        """
        Generate dataset configuration from natural language description.
        
        Args:
            user_prompt: User's natural language request
            system_prompt_path: Path to system prompt file (optional)
        
        Returns:
            Dict containing the parsed configuration
        
        Raises:
            ValueError: If LLM response is invalid
            Exception: If API call fails
        """
        # Load system prompt
        if system_prompt_path is None:
            # Default to generation.txt in config/prompts
            system_prompt_path = Path(__file__).parent.parent.parent / "config" / "prompts" / "generation.txt"
        
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        # Call LLM
        try:
            if self.provider in ["openai", "deepseek"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}  # Force JSON output
                )
                
                content = response.choices[0].message.content
            else:
                raise NotImplementedError(f"Provider {self.provider} not implemented")
            
            # Parse JSON
            try:
                config = json.loads(content)
                return config
            except json.JSONDecodeError as e:
                raise ValueError(f"LLM returned invalid JSON: {e}\nContent: {content}")
        
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def validate_and_fix_config(self, config: Dict) -> Dict:
        """
        Use LLM to validate and potentially fix a configuration.
        
        Args:
            config: Configuration dictionary to validate
        
        Returns:
            Validated/fixed configuration
        """
        # This could be enhanced to use LLM for validation
        # For now, just return the config as-is
        return config


if __name__ == "__main__":
    # Quick test
    client = LLMClient()
    test_prompt = "Generate 1000 transactions for a small grocery store with 100 items"
    
    try:
        config = client.generate_config(test_prompt)
        print("Generated configuration:")
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"Error: {e}")
