"""Template rendering with Jinja2."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from .exceptions import TemplateNotFoundError, TemplateRenderError


class TemplateRenderer:
    """Jinja2-based template renderer with support for includes and custom filters."""

    def __init__(
        self,
        template_dir: Union[str, Path],
        autoescape: bool = False,
        trim_blocks: bool = True,
        lstrip_blocks: bool = True,
    ):
        """Initialize the template renderer.

        Args:
            template_dir: Directory containing template files
            autoescape: Whether to enable autoescaping (for HTML)
            trim_blocks: Remove first newline after template tag
            lstrip_blocks: Strip leading spaces and tabs from start of line
        """
        self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise TemplateNotFoundError(
                f"Template directory not found: {self.template_dir}"
            )

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=autoescape,
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks,
        )

        # Register custom filters
        self._register_filters()

    def _register_filters(self) -> None:
        """Register custom Jinja2 filters."""

        def render_include(template_name: str, **kwargs: Any) -> str:
            """Custom filter to render included templates with parameters.

            Usage in template:
                {{ 'common/risk_management.jinja2' | render(max_risk=2.0) }}
            """
            try:
                template = self.env.get_template(template_name)
                return template.render(**kwargs)
            except TemplateNotFound:
                raise TemplateNotFoundError(f"Include template not found: {template_name}")
            except Exception as e:
                raise TemplateRenderError(f"Error rendering include {template_name}: {e}")

        self.env.filters['render'] = render_include

    def get_template(self, template_path: str) -> Template:
        """Get a template by path.

        Args:
            template_path: Path to template relative to template_dir

        Returns:
            Jinja2 Template object

        Raises:
            TemplateNotFoundError: If template doesn't exist
        """
        try:
            return self.env.get_template(template_path)
        except TemplateNotFound:
            raise TemplateNotFoundError(
                f"Template not found: {template_path} in {self.template_dir}"
            )

    def render(
        self,
        template_path: str,
        **parameters: Any
    ) -> str:
        """Render a template with parameters.

        Args:
            template_path: Path to template relative to template_dir
            **parameters: Template variables

        Returns:
            Rendered template string

        Raises:
            TemplateNotFoundError: If template doesn't exist
            TemplateRenderError: If rendering fails
        """
        try:
            template = self.get_template(template_path)
            return template.render(**parameters)
        except TemplateNotFoundError:
            raise
        except Exception as e:
            raise TemplateRenderError(
                f"Error rendering template {template_path}: {e}"
            )

    def render_string(self, template_string: str, **parameters: Any) -> str:
        """Render a template from a string.

        Args:
            template_string: Template content as string
            **parameters: Template variables

        Returns:
            Rendered template string

        Raises:
            TemplateRenderError: If rendering fails
        """
        try:
            template = self.env.from_string(template_string)
            return template.render(**parameters)
        except Exception as e:
            raise TemplateRenderError(f"Error rendering template string: {e}")

    def list_templates(self, pattern: Optional[str] = None) -> List[str]:
        """List available templates.

        Args:
            pattern: Optional glob pattern to filter templates

        Returns:
            List of template paths
        """
        if pattern:
            return [
                str(p.relative_to(self.template_dir))
                for p in self.template_dir.rglob(pattern)
                if p.is_file()
            ]
        else:
            return self.env.list_templates()


class VersionedTemplateRenderer(TemplateRenderer):
    """Template renderer with version management support."""

    def __init__(
        self,
        template_dir: Union[str, Path],
        version_pattern: str = "{type}/{version}.jinja2",
        **kwargs: Any
    ):
        """Initialize versioned template renderer.

        Args:
            template_dir: Directory containing template files
            version_pattern: Pattern for version file paths
                Example: "{type}/{version}.jinja2" -> "system/v1.jinja2"
            **kwargs: Additional arguments for TemplateRenderer
        """
        super().__init__(template_dir, **kwargs)
        self.version_pattern = version_pattern

    def render_versioned(
        self,
        template_type: str,
        version: str,
        **parameters: Any
    ) -> str:
        """Render a versioned template.

        Args:
            template_type: Type of template (e.g., "system", "user")
            version: Version identifier (e.g., "v1", "v2")
            **parameters: Template variables

        Returns:
            Rendered template string
        """
        template_path = self.version_pattern.format(
            type=template_type,
            version=version
        )
        return self.render(template_path, **parameters)

    def list_versions(self, template_type: str) -> List[str]:
        """List available versions for a template type.

        Args:
            template_type: Type of template (e.g., "system", "user")

        Returns:
            List of version identifiers
        """
        pattern = f"{template_type}/*.jinja2"
        templates = self.list_templates(pattern)

        versions = []
        for template_path in templates:
            # Extract version from filename
            filename = Path(template_path).stem
            versions.append(filename)

        return sorted(versions)

    def get_latest_version(self, template_type: str) -> Optional[str]:
        """Get the latest version for a template type.

        Args:
            template_type: Type of template

        Returns:
            Latest version identifier or None if no versions found
        """
        versions = self.list_versions(template_type)
        if not versions:
            return None

        # Assume versions are sortable (e.g., v1, v2, v10)
        # This simple sort works for most cases
        return versions[-1]
