"""Constants for the GCE Ecodevices RT2 component."""

DOMAIN = "ecodevices_rt2"

CONTROLLER = "controller"
COORDINATOR = "coordinator"
CONFIG = "config"

CONF_STATE_CLASS = "state_class"
CONF_DEVICE_CLASS = "device_class"

UNDO_UPDATE_LISTENER = "undo_update_listener"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_UPDATE_AFTER_SWITCH = 0.1
CONF_UPDATE_AFTER_SWITCH = "update_after_switch"

DEFAULT_ICON_SWITCH = "mdi:toggle-switch"
DEFAULT_ICON_CURRENCY = "mdi:currency-eur"
DEFAULT_ICON_ENERGY = "mdi:flash"
DEFAULT_ICON_HEATER = "mdi:radiator"

PRESET_COMFORT_1 = "Comfort-1"
PRESET_COMFORT_2 = "Comfort-2"


CONF_API_RESPONSE_ENTRY = "status"
CONF_API_RESPONSE_SUCCESS_VALUE = "Success"
CONF_API_GET = "api_get"
CONF_API_GET_VALUE = "api_get_value"
CONF_API_GET_ENTRY = "api_get_entry"
CONF_API_ON_GET = "api_on_get"
CONF_API_ON_GET_VALUE = "api_on_get_value"
CONF_API_OFF_GET = "api_off_get"
CONF_API_OFF_GET_VALUE = "api_off_get_value"

CONF_DEVICES = "devices"
CONF_COMPONENT = "component"
CONF_TYPE = "type"
CONF_ID = "id"
CONF_SUBPOST_ID = "subpost"
CONF_ZONE_ID = "zone"
CONF_MODULE_ID = "module"
CONF_UNIT_PRICE = "price_unit_of_measurement"
CONF_UNIT_INDEX = "index_unit_of_measurement"
CONF_UNIT_INSTANT = "instant_unit_of_measurement"
CONF_UNIT_HUMIDITY = "humidity_unit_of_measurement"
CONF_UNIT_TEMPERATURE = "temperature_unit_of_measurement"
CONF_UNIT_ILLUMINANCE = "illuminance_unit_of_measurement"
CONF_ICON_PRICE = "price_icon"
CONF_ICON_INDEX = "index_icon"
CONF_ICON_INSTANT = "instant_icon"
CONF_ICON_HUMIDITY = "humidity_icon"
CONF_ICON_TEMPERATURE = "temperature_icon"
CONF_ICON_ILLUMINANCE = "illuminance_icon"

CONF_ALLOW_ZERO = "allow_zero"

TYPE_API = "api"
TYPE_COUNTER = "counter"
TYPE_DIGITALINPUT = "digitalinput"
TYPE_ENOCEAN = "enocean"
TYPE_POST = "post"
TYPE_RELAY = "relay"
TYPE_SUPPLIERINDEX = "supplierindex"
TYPE_TOROID = "toroid"
TYPE_VIRTUALOUTPUT = "virtualoutput"
TYPE_X4FP = "x4fp"
TYPE_XTHL = "xthl"

CONF_TYPE_COMPONENT_NEEDED = {
    TYPE_API: {
        "default": "sensor",
        "parameters": {
            "sensor": [
                CONF_API_GET,
                CONF_API_GET_VALUE,
                CONF_API_GET_ENTRY,
            ],
            "switch": [
                CONF_API_GET,
                CONF_API_GET_VALUE,
                CONF_API_GET_ENTRY,
                CONF_API_ON_GET,
                CONF_API_ON_GET_VALUE,
                CONF_API_OFF_GET,
                CONF_API_OFF_GET_VALUE,
            ],
            "light": [
                CONF_API_GET,
                CONF_API_GET_VALUE,
                CONF_API_GET_ENTRY,
                CONF_API_ON_GET,
                CONF_API_ON_GET_VALUE,
                CONF_API_OFF_GET,
                CONF_API_OFF_GET_VALUE,
            ],
        },
    },
    TYPE_COUNTER: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],
        },
    },
    TYPE_DIGITALINPUT: {
        "default": "binary_sensor",
        "parameters": {
            "binary_sensor": [CONF_ID],
        },
    },
    TYPE_ENOCEAN: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],
            "switch": [CONF_ID],
            "light": [CONF_ID],
        },
    },
    TYPE_POST: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],  # CONF_SUBPOST_ID
        },
    },
    TYPE_RELAY: {
        "default": "switch",
        "parameters": {
            "switch": [CONF_ID],
            "light": [CONF_ID],
        },
    },
    TYPE_SUPPLIERINDEX: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],
        },
    },
    TYPE_TOROID: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],
        },
    },
    TYPE_VIRTUALOUTPUT: {
        "default": "switch",
        "parameters": {
            "switch": [CONF_ID],
            "light": [CONF_ID],
        },
    },
    TYPE_X4FP: {
        "default": "climate",
        "parameters": {
            "climate": [CONF_MODULE_ID, CONF_ZONE_ID],
            "switch": [CONF_MODULE_ID, CONF_ZONE_ID],
        },
    },
    TYPE_XTHL: {
        "default": "sensor",
        "parameters": {
            "sensor": [CONF_ID],
        },
    },
}
