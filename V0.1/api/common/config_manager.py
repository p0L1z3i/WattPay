"""
Configuration management module for the WattPay application.

This module provides a centralized configuration management with support for:
- Loading configuration from INI files.
- Environment variable overrides.
- Type-safe access to configuration parameters.
- Environment-specific configurations.
"""

import os
import configparser
from urllib.parse import quote_plus
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

from .log.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Dataclass for setting database configuration parameters."""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str
    pool_size: int
    pool_overflow: int
    pool_timeout: int
    connection_timeout: int

    @property
    def url(self) -> str:
        """Generate database URL for SQLAlchemy (async via asyncpg)."""
        if self.username and self.password:
            # URL-encode the password to handle special characters
            encoded_password = quote_plus(self.password)
            return (
                f"postgresql+asyncpg://{self.username}:"
                f"{encoded_password}@{self.host}:{self.port}/"
                f"{self.database}"
            )
        elif self.username and not self.password:
            # Enforce password protection when a username is provided.
            # Refuse to construct a URL without a password.
            raise ValueError(
                "Database password is required when username is set."
            )
        else:
            return (
                f"postgresql+asyncpg://{self.host}:"
                f"{self.port}/{self.database}"
            )


class ServiceConfig:
    """
    Service configuration settings.
    Dynamic access to all service settings.
    """

    def __init__(self, config_dict: dict[str, Any]):
        """Initialize with service configuration from [service] section."""
        self._config = config_dict

    def __getattr__(self, name: str) -> Any:
        """Dynamically access service configuration value from the
        [service] section."""
        if name in self._config:
            # try convert to int if it looks like port number
            value = self._config[name]
            # if name.endswith('_port') or name.endswith('_timeout'):
            if name.endswith('port') or name.endswith('_timeout'):
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return value
            # Try to convert to boolean if it looks like a boolean
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            return value
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __getitem__(self, key: str):
        """Allow dictionary-like access to service configuration."""
        return getattr(self, key)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value with default."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def keys(self) -> list[str]:
        """Return all available configuration keys."""
        return list(self._config.keys())


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str
    log_file: str
    console_output: bool
    file_output: bool
    format: str
    debug: bool


class ConfigManager:
    """Centralized configuration manager for the application."""

    APP_CONFIG_FILE = 'app.ini'

    def __init__(self, config_file: Optional[str] = None):
        self._config = configparser.ConfigParser()
        self._config_file = config_file or self._find_default_config_file()
        self._load_config()
        logger.info("Configuration loaded from app.ini")
        logger.debug("Configuration path: %s", self._config_file)

    def _find_default_config_file(self) -> str:
        """Find the default configuration file in predefined locations."""

        # Check environment variable first
        if env_config := os.getenv("APP_CONFIG_FILE"):
            if Path(env_config).exists():
                return env_config

            logger.warning(
                "Warning: Config file from APP_CONFIG_FILE "
                "does not exist: %s",
                env_config
            )

        # Determine base paths relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logger.debug("Current directory: %s", current_dir)
        project_root = os.path.dirname(os.path.dirname(current_dir))
        logger.debug("Project root: %s", project_root)

        possible_paths = [
            Path(f"{project_root}/{self.APP_CONFIG_FILE}"),
            Path(f"{current_dir}/{self.APP_CONFIG_FILE}"),
            Path(f"{project_root}/config/{self.APP_CONFIG_FILE}"),
            Path(f"{current_dir}/config/{self.APP_CONFIG_FILE}"),
            Path(f"{self.APP_CONFIG_FILE}")
        ]

        for path in possible_paths:
            if path.exists():
                return path

        raise FileNotFoundError(
            "No configuration file found. Please create app.ini "
            "or set the APP_CONFIG_FILE environment variable."
        )

    def _load_config(self):
        """Load the configuration from the file."""

        config_path = Path(self._config_file)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self._config_file}"
            )

        try:
            self._config.read(self._config_file)
            logger.debug(
                "Configuration successfully read from %s",
                self._config_file
            )
        except configparser.Error as e:
            logger.error("Error reading configuration file: %s", e)

    def _get_env_override(self, section: str, key: str):
        """Get environment variable override for config value."""

        env_key = f"APP_{section.upper()}_{key.upper()}"
        logger.debug("Checking for environment override: %s", env_key)

        if value := os.getenv(env_key):
            masked = '****' if 'password' in key.lower() else value
            logger.debug("Using environment override %s=%s", env_key, masked)
            return value
        logger.debug("No environment override found for %s", env_key)

        # Try legacy environment variables for backward capability
        legacy_mapping = {
            ("database", "host"): "POSTGRES_HOST",
            ("database", "port"): "POSTGRES_PORT",
            ("database", "database"): "POSTGRES_DB",
            ("database", "username"): "POSTGRES_USER",
            ("database", "password"): "POSTGRES_PASSWORD",
        }

        if legacy_env := legacy_mapping.get((section, key)):
            if value := os.getenv(legacy_env):
                masked = '****' if 'password' in key.lower() else value
                logger.debug(
                    "Using legacy environment override %s=%s",
                    legacy_env,
                    masked,
                )
                return value

        return None

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get a configuration value with optional environment override."""

        # Check for environment variable override first
        if env_value := self._get_env_override(section, key):

            # Convert string values to appropriate types
            if isinstance(fallback, bool):
                return env_value.lower() in ('1', 'true', 'yes', 'on')

            if isinstance(fallback, int):
                try:
                    return int(env_value)
                except ValueError:
                    logger.warning(
                        "Invalid integer value for %s.%s: %s, "
                        "using fallback",
                        section,
                        key,
                        env_value
                    )
                    return fallback

            if isinstance(fallback, float):
                try:
                    return float(env_value)
                except ValueError:
                    logger.warning(
                        "Invalid float value for %s.%s: %s, "
                        "using fallback",
                        section,
                        key,
                        env_value
                    )
                    return fallback

            return env_value

        # Get from config file
        try:
            fallback_str = (
                str(fallback) if fallback is not None else None
            )
            value = self._config.get(section, key, fallback=fallback_str)

            if value is None:
                return fallback

            if isinstance(fallback, bool):
                return value.lower() in ('1', 'true', 'yes', 'on')

            if isinstance(fallback, int):
                try:
                    return int(value)
                except ValueError:
                    logger.warning(
                        "Invalid integer value in config for %s.%s: %s, "
                        "using fallback",
                        section,
                        key,
                        value
                    )
                    return fallback

            if isinstance(fallback, float):
                try:
                    return float(value)
                except ValueError:
                    logger.warning(
                        "Invalid float value in config for %s.%s: %s, "
                        "using fallback",
                        section,
                        key,
                        value
                    )
                    return fallback
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            logger.error(
                "Configuration key not found: [%s] %s, "
                "using fallback: %s",
                section,
                key,
                fallback
            )
            return fallback

    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration as a DatabaseConfig object."""
        db_section = 'database'
        return DatabaseConfig(
            host=self.get(db_section, 'host', 'localhost'),
            port=self.get(db_section, 'port', 5432),
            database=self.get(db_section, 'name', 'watt_pay_db'),
            username=self.get(db_section, 'user', 'postgres'),
            password=self.get(db_section, 'password', ''),
            ssl_mode=self.get(db_section, 'ssl_mode', 'disable'),
            pool_size=self.get(db_section, 'pool_size', 10),
            pool_overflow=self.get(db_section, 'pool_overflow', 20),
            pool_timeout=self.get(db_section, 'pool_timeout', 30),
            connection_timeout=self.get(db_section, 'connection_timeout', 30)
        )

    @property
    def services(self) -> ServiceConfig:
        """Get service configuration with environment variable overrides."""

        services_dict = {}
        service_section_dict = {}
        service_section = 'service'

        if self._config and self._config.has_section(service_section):
            service_section_dict = dict(self._config[service_section])
            logger.debug(
                "Loaded service configuration from [%s] section: %s",
                service_section,
                service_section_dict
            )

        defaults: dict[str, str] = {
            'host': 'localhost',
            'port':     8000,
        }

        # Apply defaults for missing keys
        for key, default_value in defaults.items():
            if key in service_section_dict:
                services_dict[key] = service_section_dict[key]
            else:
                services_dict[key] = default_value

        # Apply environment variable overrides for all service config keys
        for key in services_dict:
            if env_override := self._get_env_override(service_section, key):
                services_dict[key] = env_override
                logger.debug(
                    "Applied environment override for service.%s: %s",
                    key,
                    env_override
                )

        return ServiceConfig(services_dict)

    @property
    def logging_config(self) -> LoggingConfig:
        """Get logging configuration"""

        log_section = 'logging'

        # Handle the format string to avoid ConfigParser interpolation issues
        format_str = self.get(
            log_section,
            'format',
            "%%(asctime)s | %%(levelname)s | %%(filename)s | "
            "%%(funcName)s | %%(message)s"
        )
        # Convert double %% to single %
        format_str = format_str.replace("%%", "%")

        return LoggingConfig(
            level=self.get(log_section, 'level', 'INFO'),
            log_file=self.get(log_section, 'log_file', 'build/logs/app.log'),
            console_output=self.get(log_section, 'console_output', True),
            file_output=self.get(log_section, 'file_output', True),
            format=format_str,
            debug=self.get(log_section, 'debug', False)
        )

    @property
    def environment(self) -> str:
        """Get the current application environment."""
        return self.get('DEFAULT', 'environment', 'local')

    @property
    def app_name(self) -> str:
        """Get the application name."""
        return self.get('DEFAULT', 'name', 'WattPay')

    @property
    def app_version(self) -> str:
        """Get the application version."""
        return self.get('DEFAULT', 'version', '0.0.1')

    def detect_environment(self) -> str:
        """
        - Detect the current environment based on config and environment
          variables.
        - Supported environments: local, development, production
        """
        # Priority: env variable > config file
        if env := os.getenv("APP_DEFAULT_ENVIRONMENT"):
            if env.lower() == 'local':
                return 'local'
            return env

        env = self.get('DEFAULT', 'environment', 'local')
        if env and env.lower() == 'local':
            return 'local'
        return env

    def get_config_summary(self) -> dict[str, Any]:
        """
        Get a summary of the current configuration settings for debugging.
        """
        detected_env = self.detect_environment()
        return {
            "environment": self.environment,
            "detected_environment": detected_env,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "config_file": self._config_file,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "password": '****' if self.database.password else '',
                "ssl_mode": self.database.ssl_mode,
                "pool_size": self.database.pool_size,
                "pool_overflow": self.database.pool_overflow,
                "pool_timeout": self.database.pool_timeout,
                "connection_timeout": self.database.connection_timeout,
            },
            "service": {
                "service_host": getattr(
                    self.services, 'host', 'localhost'
                ),
            },
            "logging": {
                "logging_level": self.logging_config.level,
                "log_file": self.logging_config.log_file,
                "console_output": self.logging_config.console_output,
                "file_output": self.logging_config.file_output,
                "format": self.logging_config.format,
            },
            "service_urls": self.service_urls,
        }

    @property
    def service_urls(self) -> dict[str, Any]:
        """Get constructed service URLs based on current configuration."""

        detected_env = self.detect_environment()
        service_host = getattr(self.services, 'host', 'localhost')

        # Use remote URLs for deployment environments(development, production)
        if (detected_env in ['development', 'production'] or
                service_host.startswith('http')):
            base_host = service_host
            if (base_host.startswith('http://') or
                    base_host.startswith('https://')):
                base_url = base_host.rstrip('/')
                protocol = ("https" if base_url.startswith('https://')
                            else "http")
            else:
                protocol = "https"
                base_url = f"{protocol}://{base_host}"
            logger.info(
                "Using remote service URLs (%s) with base: %s",
                detected_env,
                base_url
            )
            return {
                "api_url": f"{base_url}/api",
            }
        logger.debug("Using local development service URL")
        return {
            "api_url": f"http://localhost:{self.services.port}/api",
        }

    @property
    def api_headers(self) -> dict[str, Any]:
        """Get API headers for service calls."""
        return {
            "Content-Type": self.get(
                'api', 'content_type', 'application/json'
            ),
            "Accept": "application/json",
            "User-Agent": f"{self.app_name}/{self.app_version}",
        }


# Global configuration instance
config = ConfigManager()
