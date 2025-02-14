"""Support for the GCE Ecodevices RT2."""  # fmt: skip
import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_API_KEY
from homeassistant.const import CONF_DEVICE_CLASS
from homeassistant.const import CONF_HOST
from homeassistant.const import CONF_ICON
from homeassistant.const import CONF_NAME
from homeassistant.const import CONF_PORT
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.const import CONF_UNIT_OF_MEASUREMENT
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from pyecodevices_rt2 import EcoDevicesRT2
from pyecodevices_rt2.exceptions import EcoDevicesRT2ConnectError

from .const import CONF_ALLOW_ZERO
from .const import CONF_API_GET
from .const import CONF_API_GET_ENTRY
from .const import CONF_API_GET_VALUE
from .const import CONF_API_OFF_GET
from .const import CONF_API_OFF_GET_VALUE
from .const import CONF_API_ON_GET
from .const import CONF_API_ON_GET_VALUE
from .const import CONF_COMPONENT
from .const import CONF_DEVICES
from .const import CONF_ICON_HUMIDITY
from .const import CONF_ICON_ILLUMINANCE
from .const import CONF_ICON_INDEX
from .const import CONF_ICON_INSTANT
from .const import CONF_ICON_PRICE
from .const import CONF_ICON_TEMPERATURE
from .const import CONF_ID
from .const import CONF_MODULE_ID
from .const import CONF_SUBPOST_ID
from .const import CONF_TYPE
from .const import CONF_TYPE_COMPONENT_NEEDED
from .const import CONF_UNIT_HUMIDITY
from .const import CONF_UNIT_ILLUMINANCE
from .const import CONF_UNIT_INDEX
from .const import CONF_UNIT_INSTANT
from .const import CONF_UNIT_PRICE
from .const import CONF_UNIT_TEMPERATURE
from .const import CONF_UPDATE_AFTER_SWITCH
from .const import CONF_ZONE_ID
from .const import CONTROLLER
from .const import COORDINATOR
from .const import DEFAULT_SCAN_INTERVAL
from .const import DEFAULT_UPDATE_AFTER_SWITCH
from .const import DOMAIN
from .const import UNDO_UPDATE_LISTENER

PLATFORMS = [
    Platform.SWITCH,
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
]

# from homeassistant.components.sensor import CONF_STATE_CLASS
CONF_STATE_CLASS = "state_class"

_LOGGER = logging.getLogger(__name__)

DEVICE_CONFIG_SCHEMA_ENTRY = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_TYPE): cv.string,
        vol.Optional(CONF_COMPONENT): cv.string,
        vol.Optional(CONF_ID): cv.positive_int,
        vol.Optional(CONF_ALLOW_ZERO): cv.boolean,
        vol.Optional(CONF_ZONE_ID): cv.positive_int,
        vol.Optional(CONF_SUBPOST_ID): cv.positive_int,
        vol.Optional(CONF_MODULE_ID): cv.positive_int,
        vol.Optional(CONF_API_GET): cv.string,
        vol.Optional(CONF_API_GET_VALUE): cv.string,
        vol.Optional(CONF_API_GET_ENTRY): cv.string,
        vol.Optional(CONF_API_ON_GET): cv.string,
        vol.Optional(CONF_API_ON_GET_VALUE): cv.string,
        vol.Optional(CONF_API_OFF_GET): cv.string,
        vol.Optional(CONF_API_OFF_GET_VALUE): cv.string,
        vol.Optional(CONF_ICON): cv.icon,
        vol.Optional(CONF_DEVICE_CLASS): cv.string,
        vol.Optional(CONF_STATE_CLASS): cv.string,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_UNIT_PRICE): cv.string,
        vol.Optional(CONF_UNIT_INDEX): cv.string,
        vol.Optional(CONF_UNIT_HUMIDITY): cv.string,
        vol.Optional(CONF_UNIT_TEMPERATURE): cv.string,
        vol.Optional(CONF_UNIT_ILLUMINANCE): cv.string,
        vol.Optional(CONF_UNIT_INSTANT): cv.string,
        vol.Optional(CONF_ICON_PRICE): cv.string,
        vol.Optional(CONF_ICON_INDEX): cv.string,
        vol.Optional(CONF_ICON_INSTANT): cv.string,
        vol.Optional(CONF_ICON_HUMIDITY): cv.string,
        vol.Optional(CONF_ICON_TEMPERATURE): cv.string,
        vol.Optional(CONF_ICON_ILLUMINANCE): cv.string,
    }
)

GATEWAY_CONFIG = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=80): cv.port,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int,
        vol.Optional(CONF_DEVICES, default=[]): vol.All(
            cv.ensure_list, [DEVICE_CONFIG_SCHEMA_ENTRY]
        ),
        vol.Optional(
            CONF_UPDATE_AFTER_SWITCH, default=DEFAULT_UPDATE_AFTER_SWITCH
        ): cv.positive_float,
    },
    extra=vol.ALLOW_EXTRA,
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [GATEWAY_CONFIG])},
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the GCE Ecodevices RT2 from config file."""
    hass.data.setdefault(DOMAIN, {})

    if DOMAIN in config:
        for gateway in config.get(DOMAIN):
            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=gateway
                )
            )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the GCE Ecodevices RT2."""
    hass.data.setdefault(DOMAIN, {})

    ecort2 = EcoDevicesRT2(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        apikey=entry.data[CONF_API_KEY],
        cached_ms=entry.data[CONF_SCAN_INTERVAL] * 1000 * 10,
    )

    try:
        if not await hass.async_add_executor_job(ecort2.ping):
            raise EcoDevicesRT2ConnectError()
    except EcoDevicesRT2ConnectError as exception:
        _LOGGER.error(
            "Cannot connect to the GCE Ecodevices RT2 named %s, check host, port or api_key",
            entry.data[CONF_NAME],
        )
        raise ConfigEntryNotReady from exception
    else:
        ecort2._cached_ms = -1

    async def async_update_data():
        """Fetch cached data from API."""
        try:
            return await hass.async_add_executor_job(ecort2.get_all_cached)
        except EcoDevicesRT2ConnectError as exception:
            raise UpdateFailed("Authentication error on Ecodevices RT2") from exception

    scan_interval = int(entry.data.get(CONF_SCAN_INTERVAL))

    if scan_interval < DEFAULT_SCAN_INTERVAL:
        _LOGGER.warning(
            "A scan interval too low has been set, you probably will get errors since the GCE Ecodevices RT2 can't handle too much request at the same time"
        )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
        request_refresh_debouncer=Debouncer(
            hass,
            _LOGGER,
            cooldown=entry.data.get(CONF_UPDATE_AFTER_SWITCH),
            immediate=False,
        ),
    )
    # await coordinator.async_config_entry_first_refresh()
    # await coordinator._async_update_data()
    await coordinator.async_refresh()

    undo_listener = entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][entry.entry_id] = {
        CONF_NAME: entry.data[CONF_NAME],
        CONTROLLER: ecort2,
        COORDINATOR: coordinator,
        CONF_DEVICES: {},
        UNDO_UPDATE_LISTENER: undo_listener,
    }

    # Create the GCE Ecodevices RT2 device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, ecort2.host)},
        manufacturer="GCE",
        model="Ecodevices RT2",
        name=entry.data[CONF_NAME],
        configuration_url=f"http://{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}",
    )

    if CONF_DEVICES not in entry.data:
        _LOGGER.warning(
            "No devices configuration found for the GCE Ecodevices RT2 %s",
            entry.data[CONF_NAME],
        )
        return True

    # Load each supported component entities from their devices
    devices = build_device_list(entry.data[CONF_DEVICES])

    for component in PLATFORMS:
        _LOGGER.debug("Load component %s.", component)
        hass.data[DOMAIN][entry.entry_id][CONF_DEVICES][component] = filter_device_list(
            devices, component
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    for component in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, component)

    del hass.data[DOMAIN]

    return True


async def _async_update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


def build_device_list(devices_config: list) -> list:
    """Check and build device list from config."""
    _LOGGER.debug("Check and build devices configuration")

    devices = []
    for device_config in devices_config:
        _LOGGER.debug("Read device name: %s", device_config.get(CONF_NAME))

        # Check if TYPE is defined
        if device_config[CONF_TYPE] not in CONF_TYPE_COMPONENT_NEEDED:
            _LOGGER.error(
                "Device '%s' skipped: '%s' defined by '%s' not correct or supported.",
                device_config[CONF_NAME],
                CONF_TYPE,
                device_config[CONF_TYPE],
            )
            continue
        else:
            conf_default_allowed = CONF_TYPE_COMPONENT_NEEDED[device_config[CONF_TYPE]]
            # Define/Get component if not set, using default value
            if CONF_COMPONENT not in device_config:
                device_config[CONF_COMPONENT] = conf_default_allowed["default"]
            component = device_config[CONF_COMPONENT]

            # Test if all needed parameters are sets
            param_ok = True
            for param in conf_default_allowed["parameters"][component]:
                if param not in device_config:
                    param_ok = False
                    _LOGGER.error(
                        "Device '%s' skipped: '%s' must have '%s' set.",
                        device_config[CONF_NAME],
                        component,
                        param,
                    )
            if not param_ok:
                continue

        devices.append(device_config)
        _LOGGER.info(
            "Device '%s' added (component: '%s').",
            device_config[CONF_NAME],
            device_config[CONF_COMPONENT],
        )
    return devices


def filter_device_list(devices: list, component: str) -> list:
    """Filter device list by component."""
    return list(filter(lambda d: d[CONF_COMPONENT] == component, devices))
