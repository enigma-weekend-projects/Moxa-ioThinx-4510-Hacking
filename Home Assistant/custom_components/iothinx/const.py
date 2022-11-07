# Base
DOMAIN = 'iothinx'

CONF_DEFAULT_VALUE = 'default_value'
CONF_IO_NUM = 'io_num'
CONF_MIN_LEVEL = 'min_level'
CONF_MAX_LEVEL = 'max_level'

DEFAULT_NAME = "IoThinx"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = "161"
DEFAULT_VALUE = False
DEFAULT_UNIT_OF_MEASUREMENT = 'mA'
DEFAULT_PAYLOAD_ON = 1
DEFAULT_PAYLOAD_OFF = 0
DEFAULT_MIN_LEVEL = 4
DEFAULT_MAX_LEVEL = 20

# SNMP
CONF_BASEOID = 'baseoid'
CONF_COMMUNITY = 'dimmer-card'
CONF_VERSION = 'version'
CONF_AUTH_KEY = 'auth_key'
CONF_AUTH_PROTOCOL = 'auth_protocol'
CONF_PRIV_KEY = 'priv_key'
CONF_PRIV_PROTOCOL = 'priv_protocol'

DEFAULT_COMMUNITY = 'public'
DEFAULT_VERSION = '1'
DEFAULT_AUTH_PROTOCOL = 'none'
DEFAULT_PRIV_PROTOCOL = 'none'

MAP_VERSIONS = {"1": 0, "2c": 1, "3": None}

MAP_AUTH_PROTOCOLS = {
    "none": "usmNoAuthProtocol",
    "hmac-md5": "usmHMACMD5AuthProtocol",
    "hmac-sha": "usmHMACSHAAuthProtocol",
    "hmac128-sha224": "usmHMAC128SHA224AuthProtocol",
    "hmac192-sha256": "usmHMAC192SHA256AuthProtocol",
    "hmac256-sha384": "usmHMAC256SHA384AuthProtocol",
    "hmac384-sha512": "usmHMAC384SHA512AuthProtocol",
}

MAP_PRIV_PROTOCOLS = {
    "none": "usmNoPrivProtocol",
    "des": "usmDESPrivProtocol",
    "3des-ede": "usm3DESEDEPrivProtocol",
    "aes-cfb-128": "usmAesCfb128Protocol",
    "aes-cfb-192": "usmAesCfb192Protocol",
    "aes-cfb-256": "usmAesCfb256Protocol",
}