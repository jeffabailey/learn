from .anthropic import AnthropicAdapter
from .aws_kiro import AWSKiroAdapter
from .base import VendorAdapter, VendorReport
from .cursor import CursorAdapter
from .gemini import GeminiAdapter
from .github_copilot import GitHubCopilotAdapter
from .openai_admin import OpenAIAdapter

ADAPTERS: list[VendorAdapter] = [
    AnthropicAdapter(),
    OpenAIAdapter(),
    GitHubCopilotAdapter(),
    CursorAdapter(),
    GeminiAdapter(),
    AWSKiroAdapter(),
]

__all__ = ["ADAPTERS", "VendorAdapter", "VendorReport"]
