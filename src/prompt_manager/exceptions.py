"""Custom exceptions for the prompt management system."""


class PromptManagerError(Exception):
    """Base exception for all prompt manager errors."""
    pass


class ConfigNotFoundError(PromptManagerError):
    """Raised when a prompt configuration file is not found."""
    pass


class ConfigValidationError(PromptManagerError):
    """Raised when a prompt configuration fails validation."""
    pass


class TemplateNotFoundError(PromptManagerError):
    """Raised when a template file is not found."""
    pass


class TemplateRenderError(PromptManagerError):
    """Raised when template rendering fails."""
    pass


class VersionNotFoundError(PromptManagerError):
    """Raised when a requested prompt version is not found."""
    pass


class ParameterValidationError(PromptManagerError):
    """Raised when template parameters fail validation."""
    pass


class CacheError(PromptManagerError):
    """Raised when cache operations fail."""
    pass
