"""Configuration loading and validation for prompts."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
from pydantic import BaseModel, Field, ValidationError

from .exceptions import ConfigNotFoundError, ConfigValidationError


class ParameterSpec(BaseModel):
    """Specification for a template parameter."""
    type: str = Field(..., description="Parameter type (str, int, float, bool, list, dict)")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    required: bool = Field(True, description="Whether this parameter is required")
    description: Optional[str] = Field(None, description="Parameter description")

    def validate_value(self, value: Any) -> Any:
        """Validate and convert a value according to the parameter spec."""
        if value is None:
            if self.required and self.default is None:
                raise ValueError(f"Required parameter is missing and has no default")
            return self.default

        # Type conversion and validation
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
        }

        if self.type not in type_map:
            raise ValueError(f"Unknown parameter type: {self.type}")

        expected_type = type_map[self.type]
        if not isinstance(value, expected_type):
            try:
                return expected_type(value)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Cannot convert value {value} to type {self.type}: {e}"
                )

        return value


class PromptMetadata(BaseModel):
    """Metadata for a prompt configuration."""
    name: str = Field(..., description="Unique identifier for this prompt")
    description: Optional[str] = Field(None, description="Human-readable description")
    author: Optional[str] = Field(None, description="Author of the prompt")
    created_at: Optional[str] = Field(None, description="Creation date")
    updated_at: Optional[str] = Field(None, description="Last update date")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    current_version: str = Field("v1", description="Current/default version to use")


class PromptConfig(BaseModel):
    """Complete configuration for a prompt."""
    metadata: PromptMetadata
    parameters: Dict[str, Union[ParameterSpec, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Parameter specifications"
    )
    llm_config: Optional[Dict[str, Any]] = Field(
        None,
        description="LLM configuration (model, temperature, etc.)"
    )
    extends: Optional[str] = Field(
        None,
        description="Path to parent config to inherit from"
    )
    includes: List[str] = Field(
        default_factory=list,
        description="Common templates to include"
    )

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to convert dict parameters to ParameterSpec."""
        converted_params = {}
        for key, value in self.parameters.items():
            if isinstance(value, dict):
                converted_params[key] = ParameterSpec(**value)
            else:
                converted_params[key] = value
        self.parameters = converted_params

    def get_parameter_spec(self, param_name: str) -> Optional[ParameterSpec]:
        """Get parameter specification by name."""
        return self.parameters.get(param_name)

    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert parameters according to specs."""
        validated = {}

        # Check all provided parameters
        for key, value in params.items():
            spec = self.get_parameter_spec(key)
            if spec is None:
                # Allow unknown parameters (flexible)
                validated[key] = value
            else:
                validated[key] = spec.validate_value(value)

        # Check for missing required parameters
        for key, spec in self.parameters.items():
            if key not in params:
                if spec.required and spec.default is None:
                    raise ValueError(f"Required parameter '{key}' is missing")
                validated[key] = spec.default

        return validated


class ConfigLoader:
    """Loader for prompt configuration files."""

    def __init__(self, config_dir: Union[str, Path]):
        """Initialize the config loader.

        Args:
            config_dir: Directory containing prompt configuration files
        """
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise ConfigNotFoundError(f"Config directory not found: {self.config_dir}")

    def load(self, config_name: str) -> PromptConfig:
        """Load a prompt configuration by name.

        Args:
            config_name: Name of the config (without .yaml extension)

        Returns:
            PromptConfig object

        Raises:
            ConfigNotFoundError: If config file doesn't exist
            ConfigValidationError: If config validation fails
        """
        config_path = self.config_dir / f"{config_name}.yaml"

        if not config_path.exists():
            raise ConfigNotFoundError(
                f"Config file not found: {config_path}"
            )

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            if not config_data:
                raise ConfigValidationError(f"Empty config file: {config_path}")

            # Handle extends (inheritance)
            if 'extends' in config_data and config_data['extends']:
                parent_config = self.load(config_data['extends'])
                config_data = self._merge_configs(parent_config.model_dump(), config_data)

            return PromptConfig(**config_data)

        except yaml.YAMLError as e:
            raise ConfigValidationError(f"Invalid YAML in {config_path}: {e}")
        except ValidationError as e:
            raise ConfigValidationError(f"Config validation failed for {config_path}: {e}")
        except Exception as e:
            raise ConfigValidationError(f"Error loading config {config_path}: {e}")

    def _merge_configs(self, parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """Merge child config with parent config (child overrides parent).

        Args:
            parent: Parent configuration dict
            child: Child configuration dict

        Returns:
            Merged configuration dict
        """
        merged = parent.copy()

        for key, value in child.items():
            if key == 'extends':
                # Don't inherit the extends field itself
                continue
            elif key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Deep merge for nested dicts
                merged[key] = self._merge_configs(merged[key], value)
            elif key in merged and isinstance(merged[key], list) and isinstance(value, list):
                # Concatenate lists
                merged[key] = merged[key] + value
            else:
                # Override
                merged[key] = value

        return merged

    def list_configs(self) -> List[str]:
        """List all available configuration names.

        Returns:
            List of config names (without .yaml extension)
        """
        return [
            p.stem for p in self.config_dir.glob("*.yaml")
        ]
