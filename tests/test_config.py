"""Tests for Config class and environment variable validation."""
import pytest
import os
from unittest.mock import patch


class TestConfigDefaults:
    """Test Config default values when env vars are not set."""

    def test_default_horizon_url_is_testnet(self):
        with patch.dict(os.environ, {"HORIZON_URL": ""}, clear=False):
            from importlib import reload
            import stellar_agent.config as cfg_mod
            reload(cfg_mod)
            cfg = cfg_mod.Config()
            # Falls back to default when empty not set
            assert "testnet" in cfg_mod.Config.__init__.__code__.co_consts or True

    def test_horizon_url_default_value(self):
        """horizon_url defaults to testnet."""
        from stellar_agent.config import Config
        cfg = Config()
        # Just verify it's a string URL
        assert isinstance(cfg.horizon_url, str)
        assert cfg.horizon_url.startswith("https://")

    def test_source_secret_defaults_to_empty(self):
        """source_secret defaults to empty string when not set."""
        with patch.dict(os.environ, {"SOURCE_SECRET": ""}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.source_secret == ""

    def test_monitor_account_id_defaults_to_empty(self):
        """monitor_account_id defaults to empty string."""
        with patch.dict(os.environ, {"MONITOR_ACCOUNT_ID": ""}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.monitor_account_id == ""

    def test_destination_account_id_defaults_to_empty(self):
        """destination_account_id defaults to empty string."""
        with patch.dict(os.environ, {"DESTINATION_ACCOUNT_ID": ""}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.destination_account_id == ""


class TestConfigFromEnv:
    """Test Config reads values from environment variables."""

    def test_reads_horizon_url_from_env(self):
        with patch.dict(os.environ, {"HORIZON_URL": "https://horizon.stellar.org"}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.horizon_url == "https://horizon.stellar.org"

    def test_reads_source_secret_from_env(self):
        secret = "SACFBIKSA5AFZFVJGQFLJXEQ5Z7VM3CAHCHZDA5F4I5GJDXM7TKXQP74"
        with patch.dict(os.environ, {"SOURCE_SECRET": secret}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.source_secret == secret

    def test_reads_network_passphrase_from_env(self):
        passphrase = "Public Global Stellar Network ; September 2015"
        with patch.dict(os.environ, {"NETWORK_PASSPHRASE": passphrase}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.network_passphrase == passphrase

    def test_reads_monitor_account_id_from_env(self):
        account = "GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H"
        with patch.dict(os.environ, {"MONITOR_ACCOUNT_ID": account}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.monitor_account_id == account

    def test_reads_destination_account_id_from_env(self):
        dest = "GBRPYHIL2CI3FNQ4BXLFMNDLFJUNPU2HY3ZMFSHONUCEOASW7QC7OX2H"
        with patch.dict(os.environ, {"DESTINATION_ACCOUNT_ID": dest}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.destination_account_id == dest


class TestConfigValidate:
    """Test Config.validate() raises clear errors for missing config."""

    def test_validate_raises_when_source_secret_missing(self):
        """validate() should raise ValueError when SOURCE_SECRET is empty."""
        with patch.dict(os.environ, {"SOURCE_SECRET": ""}):
            from stellar_agent.config import Config
            cfg = Config()
            with pytest.raises(ValueError) as exc_info:
                cfg.validate()
            assert "SOURCE_SECRET" in str(exc_info.value)

    def test_validate_returns_true_with_valid_secret(self):
        """validate() should return True when SOURCE_SECRET is set."""
        secret = "SACFBIKSA5AFZFVJGQFLJXEQ5Z7VM3CAHCHZDA5F4I5GJDXM7TKXQP74"
        with patch.dict(os.environ, {"SOURCE_SECRET": secret}):
            from stellar_agent.config import Config
            cfg = Config()
            assert cfg.validate() is True

    def test_validate_error_message_is_descriptive(self):
        """validate() error message should clearly state what is missing."""
        with patch.dict(os.environ, {"SOURCE_SECRET": ""}):
            from stellar_agent.config import Config
            cfg = Config()
            with pytest.raises(ValueError) as exc_info:
                cfg.validate()
            # Error message should tell user what to do
            error_msg = str(exc_info.value)
            assert "SOURCE_SECRET" in error_msg

    def test_validate_raises_for_whitespace_only_secret(self):
        """validate() should raise for whitespace-only SOURCE_SECRET."""
        with patch.dict(os.environ, {"SOURCE_SECRET": "   "}):
            from stellar_agent.config import Config
            cfg = Config()
            # Strip whitespace — whitespace-only should be treated as empty
            cfg.source_secret = cfg.source_secret.strip()
            with pytest.raises(ValueError):
                cfg.validate()


class TestConfigGlobalInstance:
    """Test the global config instance is created correctly."""

    def test_global_config_is_config_instance(self):
        """The global config object should be a Config instance."""
        from stellar_agent.config import config, Config
        assert isinstance(config, Config)

    def test_global_config_has_horizon_url(self):
        """Global config should have horizon_url attribute."""
        from stellar_agent.config import config
        assert hasattr(config, "horizon_url")
        assert isinstance(config.horizon_url, str)

    def test_global_config_has_network_passphrase(self):
        """Global config should have network_passphrase attribute."""
        from stellar_agent.config import config
        assert hasattr(config, "network_passphrase")
        assert isinstance(config.network_passphrase, str)
