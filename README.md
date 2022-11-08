# Moxa ioThinx 4510 Hacking
Moxa ioThinx 4510 protocol and hacking information

Данный проект, является моими наработками в иследование устройства **Moxa ioThinx 4510**. Все приведенное здесь является общедоступным и получено в ходе реверс инжиниринга и анализа трафика.

Home Assistant [Custom components](https://github.com/enigma-weekend-projects/Moxa-ioThinx-4510-Hacking/tree/main/Home%20Assistant/) - написан в 2020 году, на текущий момент иможет быть устаревшим.

#Moxa Web API

В файле [iothinx-web-api.md](https://github.com/enigma-weekend-projects/Moxa-ioThinx-4510-Hacking/blob/main/iothinx-web-api.md) Приведен список всех найденых мной запросов, доступных через web интерфейс. Большая часть была найдена в js файлах скачиваемых при открытии страниц устройства. Для подтверждения их использовался анализ трафика при помощи wireshark (к сожалению записи не сохранились). Не все команды удалось проверить. К присмеру установку конфигураций, загрузка прошивки и сброс к заводским настройкам.

#Moxa IOLib

[iolib](https://github.com/enigma-weekend-projects/Moxa-ioThinx-4510-Hacking/tree/main/iolib) - простая библиотека для работы с ioThinx через его Web APi. Все команды и структуры данных получены из исхожного кода js фйлов, скачеваемых при открытии Web интерфейса. Сами js файлы не выкладываю по пречине возможного нарушения лицензий, приведу только список использованных:
 * auth.js - Файл где описан метод авторизаций. Самой важной частью является функция `signin` - в ней, в параметре `r` содержиться уникальны (возможно...) ключь шифрования пароля и имени пользователя. Я его извлекаю регулярным вырожением, благодаря этому ключь не нужно хранить для каждого устройства в отдельности.
 * cryptico.js - Библиотка [cryptico](https://www.npmjs.com/package/cryptico) с немного измененным (или устаревшим) кодом. Из этого файла можно узнать способ шифрования и полиномы (если они отлечаются от стандартных).
 * main.js - Основной код для общения Web интерфейса с устройствоим. Большенствой REST Api команд получены из него. так же можно найти процедуру и способ способ авторизации.
