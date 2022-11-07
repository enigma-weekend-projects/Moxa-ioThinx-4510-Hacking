import logging
import voluptuous as vol
import pysnmp.hlapi.asyncio as hlapi
import homeassistant.helpers.config_validation as cv

from datetime import timedelta
from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    UsmUserData,
    getCmd,
)

from homeassistant.components.binary_sensor import BinarySensorEntity, PLATFORM_SCHEMA, DEVICE_CLASSES
from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_ICON_TEMPLATE,
    CONF_DEVICE_CLASS,
)
from .const import (
    DOMAIN,
    CONF_BASEOID,
    CONF_IO_NUM,
    CONF_DEFAULT_VALUE,
    CONF_COMMUNITY,
    CONF_VERSION,
    CONF_AUTH_KEY,
    CONF_AUTH_PROTOCOL,
    CONF_PRIV_KEY,
    CONF_PRIV_PROTOCOL,
    DEFAULT_NAME,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_COMMUNITY,
    DEFAULT_VERSION,
    DEFAULT_AUTH_PROTOCOL,
    DEFAULT_PRIV_PROTOCOL,
    DEFAULT_VALUE,
    MAP_VERSIONS,
    MAP_AUTH_PROTOCOLS,
    MAP_PRIV_PROTOCOLS
)

logger = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_BASEOID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_IO_NUM): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
        vol.Optional(CONF_COMMUNITY, default=DEFAULT_COMMUNITY): cv.string,
        vol.Optional(CONF_VERSION, default=DEFAULT_VERSION): vol.In(MAP_VERSIONS),
        vol.Optional(CONF_USERNAME): cv.string,
        vol.Optional(CONF_AUTH_KEY): cv.string,
        vol.Optional(CONF_PRIV_KEY): cv.string,
        vol.Optional(CONF_AUTH_PROTOCOL, default=DEFAULT_AUTH_PROTOCOL): vol.In(MAP_AUTH_PROTOCOLS),
        vol.Optional(CONF_PRIV_PROTOCOL, default=DEFAULT_PRIV_PROTOCOL): vol.In(MAP_PRIV_PROTOCOLS),
        vol.Optional(CONF_DEFAULT_VALUE, default=DEFAULT_VALUE): cv.boolean,
        vol.Optional(CONF_DEVICE_CLASS): vol.In(DEVICE_CLASSES),
        vol.Optional(CONF_ICON_TEMPLATE): cv.template,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    baseoid = config.get(CONF_BASEOID)
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    io_num = config.get(CONF_IO_NUM)
    community = config.get(CONF_COMMUNITY)
    version = config.get(CONF_VERSION)
    username = config.get(CONF_USERNAME)
    auth_key = config.get(CONF_AUTH_KEY)
    priv_key = config.get(CONF_PRIV_KEY)
    auth_protocol = config.get(CONF_AUTH_PROTOCOL)
    priv_protocol = config.get(CONF_PRIV_PROTOCOL)
    default_value = config.get(CONF_DEFAULT_VALUE)
    device_class = config.get(CONF_DEVICE_CLASS)
    icon_template = config.get(CONF_ICON_TEMPLATE)

    if icon_template is not None:
        icon_template.hass = hass

    if version == '3':
        auth = UsmUserData(username, authKey=auth_key or None, privKey=priv_key or None,
                           authProtocol=getattr(hlapi, MAP_AUTH_PROTOCOLS[auth_protocol]), privProtocol=getattr(hlapi, MAP_PRIV_PROTOCOLS[priv_protocol])),
    else:
        auth = CommunityData(community, mpModel=MAP_VERSIONS[version])

    auth = [SnmpEngine(), auth, UdpTransportTarget((host, port)), ContextData()]
    baseoid, start = baseoid.rsplit('.', 1)
    start = int(start)

    if io_num is not None and type(io_num) is int:
        error, _, _, _ = await getCmd(*auth, ObjectType(ObjectIdentity(f'{baseoid}.0')))
        if error is not None:
            logger.error(f'SNMP error: {error}')
            return

        sensors = [IoThinxBinarySensor(
            name=f'{name}-DI-{str(io).zfill(2)}',
            baseoid=f'{baseoid}.{io}',
            auth=auth,
            default_value=default_value,
            device_class=device_class,
            icon_template=icon_template
        ) for io in range(start, start+io_num)]
    else:
        error, _, _, _ = await getCmd(*auth, ObjectType(ObjectIdentity(baseoid)))
        if error is not None:
            logger.error(f'SNMP error: {error}')
            return

        sensors = [IoThinxBinarySensor(
            name=f'{name}-DI-{str(start).zfill(2)}',
            baseoid=f'{baseoid}.{start}',
            auth=auth,
            default_value=default_value,
            device_class=device_class,
            icon_template=icon_template
        )]

    async_add_entities(sensors, True)


class IoThinxBinarySensor(BinarySensorEntity):
    def __init__(self, name, baseoid, auth, default_value, device_class, icon_template):
        self._name = name
        self._baseoid = baseoid
        self._auth = auth
        self._default_value = default_value
        self._device_class = device_class
        self._icon_template = icon_template

        self._value = default_value

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return f'{self.entity_id}_{self._baseoid.replace(".", "")}'

    @property
    def device_class(self) -> str:
        return self._device_class

    @property
    def is_on(self) -> bool:
        return self._value

    async def async_update(self) -> None:
        error, status, index, table = await getCmd(*self._auth, ObjectType(ObjectIdentity(self._baseoid)))

        if error:
            logger.error(f'SNMP error ({self._baseoid}): {error}')
        elif status:
            logger.error(f'SNMP error: {status.prettyPrint()} at {index and table[-1][int(index) - 1] or "?"}')

        if error or status:
            self._value = self._default_value
        else:
            for row in table:
                self._value = bool(int(row[-1]))