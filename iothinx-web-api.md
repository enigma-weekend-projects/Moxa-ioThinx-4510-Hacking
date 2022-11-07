# ioThinx Web API

Под копотом все общение между WEB интерфейсом и устрофством осуществляется при помощи REST API протокола, описанного ниже.

## Возможные параметры

**direction** - Расположение, положение группы модулей на шине, в имеющемся у меня устройстве всегда равнялось `0` но возможно при использование переходника на другой ряд (находил где то упоминание о таком) это значение будет изменено.
**slotNumber** - Номер слота. Порядковый номер модуля, отсчет начинаеться от головного модуля и лежит в диапазоне от 0 до 32 (Упоменаеться расширение до 64, но у меня не удалось протестировать это).
**port** - Номер порта. Лежит в диапазоне от 0 до 16.

## Базовые команды

| Метод | URL 							| Параметры			| Описание 												|
|-------|-------------------------------|-------------------|-------------------------------------------------------|
| GET   | `/action/time` 				|					| Текущее время 										|
| GET   | `/action/slotinfo`			|					| Информация о установленных модулях					|
| GET   | `/action/device`				|					| Информация о головном модуле							|
| GET   | `/action/moduleInfo`			| 0 - `45MR-1600`<BR>1 - `45MR-1601`<BR>2 - `45MR-2600`<BR>3 - `45MR-2601`<BR>4 - `45MR-2606`<BR>5 - `45MR-2404`<BR>6 - `45MR-3800`<BR>7 - `45MR-3810`<BR>8 - `45MR-4420`<BR>9 - `45MR-6600`<BR>10 - `45MR-6810`	| Краткая информация о типе подключенных модулях, В ответ приходит JSON с перечислениями типов модулей.		|
| GET   | `/action/device/connection`	|					| Список соединений										|
| GET   | `/action/device/systemError`	|					| Код системной ошибки									|
| GET   | `/action/system/log`			|					| Листинг лога системы (данные закодированы но можно разобрать)				|
| GET   | `/action/system/ca_export`	|					| Запрос сертификата шифрования (не ясно для чего, упоменаеться https)				|
| GET   | `/action/system/config/1`		|					| Первая половина настроек модулей (response type: arraybuffer, JSON), шифруються RSA + AES-CBC 				|
| GET   | `/action/system/config/2`		|					| Вторая половина настроек модулей						|
| GET   | `/action/system/config/3`		|					| Системные настройки									|
| GET   | `/action/system/config/4`		|					| Настройки modbus										|
| GET   | `/action/system/config/5`		|					| Настройки внутренних регистров						|
| GET   | `/action/system/config/6`		|					| Настройки serial/modbus RTU master					|
| GET   | `/action/system/config/7`		|					| Первая часть настроек MQTT							|
| GET   | `/action/system/config/8`		|					| Вторая часть настроек MQTT							|
| GET   | `/action/system/config/9`		|					| Третья часть настроек MQTT							|
| GET   | `/action/system/config/10`	|					| Четвертая часть настроек MQTT							|
| GET   | `/action/system/config/11`	|					| Настройки SNMP trap									|
| GET   | `/action/system/ITProtocolControl`			|					| Иформация о протоколах (count_max, trap, inform)				|

## Команды общения с модулями

| Метод | URL 							| Параметры			| Описание 												|
|-------|-------------------------------|-------------------|-------------------------------------------------------|
| GET   | `/action/io/{direction}/{slotNumber}`			|					| Состояние портов выбранного модуля				|
| GET   | `/action/status/{direction}/{slotNumber}`			|					| Состоянеи модуля 				|
| PUT   | `/action/device/safeMode`			|					| Переводит утройство в защищенный режим				|
| PUT   | `/action/device/settime`			|					| Установить время				|
| PUT   | `/action/system/restarting`			|					| Перезагружает устройство				|
| PUT   | `/action/io/ai/aiResetMinMaxValue/{direction}/{slotNumber}/{port}`			|					| Сброс минимальных/максимальных значений аналогового порта 				|
| PUT   | `/action/io/ao/aoValueScaled/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/di/diCounterStatus/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/di/diCounterValue/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/do/doStatus/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/relay/relayStatus/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/rtd/rtdResetMinMaxValue/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/rtd/calibration/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/tc/tcResetMinMaxValue/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/io/tc/calibration/{direction}/{slotNumber}/{port}`			|					| 				|
| PUT   | `/action/locate/{direction}/{slotNumber}`			|					| 				|

## Команды установкинастроек и авторизации

| Метод | URL 							| Параметры			| Описание 												|
|-------|-------------------------------|-------------------|-------------------------------------------------------|
| POST   | `/action/login`			|					| 				|
| POST   | `/action/logout`			|					| 				|
| POST   | `/action/slot0/firmware`			|					| 				|
| POST   | `/action/system/config`			|					| 				|
| POST   | `/action/system/sconfig/`			|					| 				|
| POST   | `/action/system/config/1`			|					| 				|
| POST   | `/action/system/config/2`			|					| 				|
| POST   | `/action/system/config/3`			|					| 				|
| POST   | `/action/system/config/4`			|					| 				|
| POST   | `/action/system/config/5`			|					| 				|
| POST   | `/action/system/config/6`			|					| 				|
| POST   | `/action/system/config/7`			|					| 				|
| POST   | `/action/system/config/8`			|					| 				|
| POST   | `/action/system/config/9`			|					| 				|
| POST   | `/action/system/config/10`			|					| 				|
| POST   | `/action/system/config/11`			|					| 				|
| DELETE   | `/action/slot0/config`			|					| Сброс к заводским настроек (но это не точно...)				|
