import re
import rsa
import enum
import attr
import json
import hashlib
import logging
import aiohttp
import asyncio

from time import monotonic
from typing import Any, List, Dict, Optional, Callable, Union, Tuple

logger = logging.getLogger(__name__)


class ModuleType(enum.Enum):
    """
    Доступные типы модулей.
    Источник: Файл main.js, строка 36, объект: o.MODULE_TYPE
    """
    MODULE_45MR_1600 = 0
    MODULE_45MR_1601 = 1
    MODULE_45MR_2600 = 2
    MODULE_45MR_2601 = 3
    MODULE_45MR_2606 = 4
    MODULE_45MR_2404 = 5
    MODULE_45MR_3800 = 6
    MODULE_45MR_3810 = 7
    MODULE_45MR_4420 = 8
    MODULE_45MR_6600 = 9
    MODULE_45MR_6810 = 10

    def __str__(self) -> str:
        if self.value == self.MODULE_45MR_1600:
            return '45MR-1600'
        elif self.value == self.MODULE_45MR_1601:
            return '45MR-1601'
        elif self.value == self.MODULE_45MR_2600:
            return '45MR-2600'
        elif self.value == self.MODULE_45MR_2601:
            return '45MR-2601'
        elif self.value == self.MODULE_45MR_2606:
            return '45MR-2606'
        elif self.value == self.MODULE_45MR_2404:
            return '45MR-2404'
        elif self.value == self.MODULE_45MR_3800:
            return '45MR-3800'
        elif self.value == self.MODULE_45MR_3810:
            return '45MR-3810'
        elif self.value == self.MODULE_45MR_4420:
            return '45MR-4420'
        elif self.value == self.MODULE_45MR_6600:
            return '45MR-6600'
        elif self.value == self.MODULE_45MR_6810:
            return '45MR-6810'


class Device:
    def __init__(self, host: str, port: int, username: str, password: str, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        """
        Создание виртуального представления Moxa ioThinx 4510.

        :param host: IP аддрес устройства.
        :param port: Порт веб интерфейса (80 или 433).
        :param username: Имя пользователя, должен иметь права Администратора или Оператора
        :param password: Пароль пользователя
        :param loop: Обработчик событий AsyncIO. Необязательный параметр
        """
        self.loop: asyncio.AbstractEventLoop = loop or asyncio.get_event_loop()
        self._host: str = host
        self._port: int = port
        self._username: str = username
        self._password: str = password

        self._https: bool = False
        """Тип соединения для запросов: http или https."""
        self._update_time: float = 0.3
        """Минимальное время обновления, предотвращает перегрузку буфира устройства."""
        self._lust_update: float = 0
        """Время последнего обновления."""
        self._jar: aiohttp.CookieJar = aiohttp.CookieJar(unsafe=True)
        """Cookie запись для хранения текущей сессий."""

        self._name: Optional[str] = None
        """Имя устройства"""
        self._module_num: Optional[int] = None
        """Число устанновленных модулей"""
        self._version: Optional[str] = None
        """Версия прошивки"""
        self._serial_num: Optional[str] = None
        """Серийный номер устройства"""
        self._device_ip: Optional[str] = None
        """IP адресс устройства"""
        self._device_mac: Optional[str] = None
        """MAC адресс устройства"""
        self._level: Optional[int] = None
        """Уровень доступа текущего пользователя"""
        self._error: Optional[int] = None
        """Текущее состояние устройства"""

        self._module_list: List[Module] = []
        """Контейнер установленных модулей"""

    @property
    def base_url(self) -> str:
        """
        Базовый адрес устройства.
        :return: Адрес для запросов. Формат (http|https)://host:port
        """
        return f'{"https" if self._https else "http"}://{self._host}:{self._port}'

    async def get(self, api_urp: str, public_api: bool = False) -> Union[str, Dict[str, Any], List[Any]]:
        async with aiohttp.ClientSession(cookie_jar=self._jar) as session:
            headers = public_api if {'Accept': 'vdn.dac.v2', 'Content-Type': 'application/json'} else None
            api_urp = api_urp.lstrip('/')
            async with session.get(f'{self.base_url}/{api_urp}', headers=headers) as response:
                if response.headers.get('Content-Type') == 'application/json':
                    return json.loads(await response.text())
                else:
                    return await response.text()

    async def post(self, api_urp: str, data: Optional[Any] = None, public_api: bool = False) -> Union[str, Dict[str, Any], List[Any]]:
        async with aiohttp.ClientSession(cookie_jar=self._jar) as session:
            headers = public_api if {'Accept': 'vdn.dac.v2', 'Content-Type': 'application/json'} else None
            api_urp = api_urp.lstrip('/')
            async with session.post(f'{self.base_url}/{api_urp}', data=data, headers=headers) as response:
                if response.headers.get('Content-Type') == 'application/json':
                    return json.loads(await response.text())
                else:
                    return await response.text()

    async def put(self, api_urp: str, data: Optional[Any] = None, public_api: bool = False) -> Union[str, Dict[str, Any], List[Any]]:
        async with aiohttp.ClientSession(cookie_jar=self._jar) as session:
            headers = public_api if {'Accept': 'vdn.dac.v2', 'Content-Type': 'application/json'} else None
            api_urp = api_urp.lstrip('/')
            async with session.put(f'{self.base_url}/{api_urp}', data=data, headers=headers) as response:
                if response.headers.get('Content-Type') == 'application/json':
                    return json.loads(await response.text())
                else:
                    return await response.text()

    async def _login(self) -> None:
        async with aiohttp.ClientSession(cookie_jar=self._jar) as session:
            async with session.get(self.base_url) as response:
                if response.status == 404:
                    raise Exception(
                        f'The requested address was not found. URL: {self._https if "http" else "https"}://{self._host}:{self._port}/\n'
                        f'{await response.text()}')

            async with session.get(f'{self.base_url}/auth.js') as response:
                find = re.findall(r'signin:function[\w\W]*r=\"([A-F,0-9]*)\"[\w\W]*n=\"(\d*)\"', await response.text())
                n: int = int(find[0][0], base=16)
                e: int = int(find[0][1], base=16)

                if n is None or e is None:
                    raise Exception('Failed to retrieve public key')

            public_key = rsa.PublicKey(n=n, e=e)
            data = json.dumps({'username': self._username, 'password': self._password})
            data = rsa.encrypt(data.encode(), pub_key=public_key)
            data_hash = hashlib.sha256(data)
            data = data + data_hash.digest()

            async with session.post(f'{self.base_url}/action/login', data=data) as response:
                if response.status != 200:
                    raise Exception(f'Failed to get authorization on the server, code: {response.status}\n'
                                    f'{await response.text()}')

    async def connect(self):
        if not self._jar:
            await self._login()
        await self._update(install=True)

    async def _update(self, install: bool = False) -> None:
        dev_info = await self.get('/action/device')
        self._name = dev_info[0]
        self._module_num = dev_info[1]
        self._version = dev_info[2]
        self._serial_num = dev_info[3]
        self._device_ip = dev_info[4]
        self._device_mac = dev_info[5]
        self._level = dev_info[6]
        self._error = dev_info[7]

        slot_info = await self.get('/action/slotinfo')
        for module_info in slot_info['infos']:
            module = Module(self, *module_info) if install else self._module_list[module_info[1]-1]

            io_info = await self.get(f'/action/io/{module.direct}/{module.slot}')

            if 'di' in io_info:
                for di_info in io_info['di']:
                    if install:
                        module.ios.append(DigitalInput(self, module, *di_info))
                    else:
                        module.ios[di_info[0]]._update(*di_info)
            if 'do' in io_info:
                for do_info in io_info['do']:
                    if install:
                        module.ios.append(DigitalOutput(self, module, *do_info))
                    else:
                        module.ios[do_info[0]]._update(*do_info)
            if 'ai' in io_info:
                for ai_info in io_info['ai']:
                    if install:
                        module.ios.append(AnalogInput(self, module, *ai_info))
                    else:
                        module.ios[ai_info[0]]._update(*ai_info)
            if 'ao' in io_info:
                for ao_info in io_info['ao']:
                    if install:
                        module.ios.append(AnalogOutput(self, module, *ao_info))
                    else:
                        module.ios[ao_info[0]]._update(*ao_info)

            self._module_list.append(module)

    async def update(self, ) -> None:
        time = monotonic() - self._lust_update
        if time > self._update_time:
            await self._update()
            self._lust_update = monotonic()
        else:
            return

    def __getitem__(self, key: Union[int, str]) -> Optional['Module']:
        if type(key) is int:
            if key < len(self._module_list):
                return self._module_list[key]
            else:
                return None
        elif type(key) is str:
            for module in self._module_list:
                if module.name == key:
                    return module
            return None
        else:
            raise TypeError('Key type not is int or str!')

    @property
    def modules(self) -> List['Module']:
        return self._module_list

    @property
    def name(self) -> str:
        return self._name

    @property
    def module_num(self) -> int:
        return self._module_num

    @property
    def version(self) -> str:
        return self._version

    @property
    def serial(self) -> str:
        return self._serial_num

    @property
    def device_ip(self) -> str:
        return self._device_ip

    @property
    def device_mac(self) -> str:
        return self._device_mac

    @property
    def user_level(self) -> int:
        return self._level

    @property
    def error(self) -> int:
        return self._error


class DigitalInput:
    def __init__(self, device: Device, module: 'Module', no: Optional[int] = None, name: Optional[str] = None,
                 mode: Optional[int] = None, value: Optional[int] = None, trigger: Optional[int] = None,
                 filter: Optional[int] = None, status: Optional[int] = None):
        self._device: Device = device
        self._module: Module = module
        self._no: Optional[int] = no
        self._name: Optional[str] = name
        self._mode: Optional[int] = mode
        self._value: Optional[bool] = value
        self._trigger: Optional[int] = trigger
        self._filter: Optional[int] = filter
        self._status: Optional[int] = status

    def _update(self, no: int, name: str, mode: int, value: int, trigger: int, filter: int, status: int) -> None:
        self._no = no
        self._name = name
        self._mode = mode
        self._value = value
        self._trigger = trigger
        self._filter = filter
        self._status = status



    @property
    def name(self) -> str:
        return self._name

    @property
    def no(self) -> int:
        return self._no

    @property
    def mode(self) -> int:
        return self._mode

    @property
    def value(self) -> Union[int, bool]:
        if self._mode:
            return self._value
        else:
            return self.status

    @property
    def trigger(self) -> int:
        return self._trigger

    @property
    def filter(self) -> int:
        return self._filter

    @property
    def status(self) -> bool:
        return bool(self._status)


class DigitalOutput:
    def __init__(self, device: Device, module: 'Module', no: Optional[int] = None, name: Optional[str] = None,
                 mode: Optional[int] = None, on_width: Optional[int] = None, off_width: Optional[int] = None,
                 value: Optional[int] = None, status: Optional[int] = None):
        self._device: Device = device
        self._module: Module = module
        self._no: Optional[int] = no
        self._name: Optional[str] = name
        self._mode: Optional[int] = mode
        self._on_width: Optional[int] = on_width
        self._off_width: Optional[int] = off_width
        self._value: Optional[int] = value
        self._status: Optional[int] = status

    def _update(self, no: int, name: str, mode: int, on_width: int, off_width: int, value: int, status: int) -> None:
        self._no = no
        self._name = name
        self._mode = mode
        self._on_width = on_width
        self._off_width = off_width
        self._value = value
        self._status = status

    @property
    def name(self) -> str:
        return self._name

    @property
    def no(self) -> int:
        return self._no

    @property
    def mode(self) -> int:
        return self._mode

    @property
    def on_width(self) -> int:
        return self._on_width

    @property
    def off_width(self) -> int:
        return self._off_width

    @property
    def value(self) -> int:
        return self._value

    @property
    def status(self) -> bool:
        return bool(self._status)

    @status.setter
    def status(self, value: bool) -> None:
        async def set_status():
            await self._device.put(f'/action/io/do/doStatus/{self._module.direct}/{self._module.slot}/{self.no}', data=f'[{1 if value else 0}]')
        self._device.loop.create_task(set_status())


class AnalogInput:
    def __init__(self, device: Device, module: 'Module', no: Optional[int] = None, name: Optional[str] = None,
                 enable: Optional[int] = None, range_min: Optional[int] = None, range_max: Optional[int] = None,
                 value: Optional[int] = None, min: Optional[int] = None, max: Optional[int] = None,
                 burnout: Optional[int] = None, unit: Optional[str] = None):
        self._device: Device = device
        self._module: Module = module
        self._no: Optional[int] = no
        self._name: Optional[str] = name
        self._enable: Optional[int] = enable
        self._range_min: Optional[float] = range_min
        self._range_max: Optional[float] = range_max
        self._value: Optional[float] = value
        self._min: Optional[float] = min
        self._max: Optional[float] = max
        self._burnout: Optional[int] = burnout
        self._unit: Optional[str] = unit

    def _update(self, no: int, name: str, enable: int, range_min: float, range_max: float, value: float, min: float, max: float, burnout: float, unit: str) -> None:
        self._no = no
        self._name = name
        self._enable = enable
        self._range_min = range_min
        self._range_max = range_max
        self._value = value
        self._min = min
        self._max = max
        self._burnout = burnout
        self._unit = unit

    @property
    def name(self) -> str:
        return self._name

    @property
    def no(self) -> int:
        return self._no

    @property
    def enable(self) -> bool:
        return bool(self._enable)

    @property
    def range_min(self) -> float:
        return self._range_min

    @property
    def range_max(self) -> float:
        return self._range_max

    @property
    def value(self) -> float:
        return self._value

    @property
    def min(self) -> float:
        return self._min

    @property
    def max(self) -> float:
        return self._max

    @property
    def burnout(self) -> float:
        return self._burnout

    @property
    def unit(self) -> str:
        return self._unit


class AnalogOutput:
    def __init__(self, device: Device, module: 'Module', no: Optional[int] = None, name: Optional[str] = None,
                 mode: Optional[int] = None, range_min: Optional[int] = None, range_max: Optional[int] = None,
                 value: Optional[int] = None, status: Optional[int] = None, unit: Optional[str] = None):
        self._device: Device = device
        self._module: Module = module
        self._no: Optional[int] = no
        self._name: Optional[str] = name
        self._mode: Optional[int] = mode
        self._range_min: Optional[float] = range_min
        self._range_max: Optional[float] = range_max
        self._value: Optional[float] = value
        self._status: Optional[int] = status
        self._unit: Optional[str] = unit

    def _update(self, no: int, name: str, mode: int, range_min: float, range_max: float, value: float, status: int, unit: str) -> None:
        self._no = no
        self._name = name
        self._mode = mode
        self._range_min = range_min
        self._range_max = range_max
        self._value = value
        self._status = status
        self._unit = unit

    @property
    def name(self) -> str:
        return self._name

    @property
    def no(self) -> int:
        return self._no

    @property
    def mode(self) -> int:
        return self._mode

    @property
    def range_min(self) -> float:
        return self._range_min

    @property
    def range_max(self) -> float:
        return self._range_max

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        async def set_value():
            await self._device.put(f'/action/io/ao/aoValueScaled/{self._module.direct}/{self._module.slot}/{self.no}', data=f'[{value}]')
        self._device.loop.create_task(set_value())

    @property
    def status(self) -> int:
        return self._status

    @property
    def unit(self) -> str:
        return self._unit


class Module:
    def __init__(self, device: Device, direct: Optional[int] = None, slot: Optional[int] = None,
                 type: Optional[int] = None, name: Optional[str] = None, version: Optional[str] = None,
                 serial: Optional[str] = None, locating: Optional[int] = None, status: Optional[int] = None):
        self._device: Device = device
        self._direct: Optional[int] = direct
        self._slot: Optional[int] = slot
        self._type: Optional[int] = type
        self._name: Optional[str] = name
        self._version: Optional[str] = version
        self._serial: Optional[str] = serial
        self._locating: Optional[str] = locating
        self._status: Optional[int] = status

        self._io: List[Union[DigitalInput, DigitalOutput, AnalogInput, AnalogOutput]] = []

    async def locate(self, on: bool) -> None:
        await self._device.put(f'/action/locate/{self._direct}/{self._slot}', [1 if on else 0])

    def __getitem__(self, key: Union[int, str]) -> Optional[Union[DigitalInput, DigitalOutput, AnalogInput, AnalogOutput]]:
        if type(key) is int:
            if key < len(self._io):
                return self._io[key]
            else:
                return None
        elif type(key) is str:
            for io in self._io:
                if io.name == key:
                    return io
            return None
        else:
            raise TypeError('Key type not is int or str!')

    @property
    def ios(self) -> List[Union[DigitalInput, DigitalOutput, AnalogInput, AnalogOutput]]:
        return self._io

    @property
    def direct(self) -> int:
        return self._direct

    @property
    def slot(self) -> int:
        return self._slot

    @property
    def type(self) -> int:
        return ModuleType(self._type)

    @property
    def str_type(self) -> str:
        return str(self.type)

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def serial(self) -> str:
        return self._serial

    @property
    def locating(self) -> bool:
        return bool(self._locating)

    @property
    def status(self) -> int:
        return self._status
