"""Test the Opensprinkler config flow."""
from pyopensprinkler import OpensprinklerAuthError, OpensprinklerConnectionError

from homeassistant import config_entries, setup
from homeassistant.components.opensprinkler.const import DOMAIN

from tests.async_mock import patch


async def test_form(hass):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.opensprinkler.config_flow.OpenSprinkler",
        return_value=True,
    ), patch(
        "homeassistant.components.opensprinkler.async_setup", return_value=True
    ) as mock_setup, patch(
        "homeassistant.components.opensprinkler.async_setup_entry", return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": "1.1.1.1", "password": "test-password"},
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == "Opensprinkler"
    assert result2["data"] == {
        "host": "1.1.1.1",
        "password": "test-password",
        "port": 8080,
        "name": "Opensprinkler",
        "run_seconds": 60,
    }
    await hass.async_block_till_done()
    assert len(mock_setup.mock_calls) == 1
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass):
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.opensprinkler.config_flow.OpenSprinkler",
        side_effect=OpensprinklerAuthError,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": "1.1.1.1", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.opensprinkler.config_flow.OpenSprinkler",
        side_effect=OpensprinklerConnectionError,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": "1.1.1.1", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.opensprinkler.config_flow.OpenSprinkler",
        side_effect=Exception,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"host": "1.1.1.1", "password": "test-password"},
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "unknown"}
