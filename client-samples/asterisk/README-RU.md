# Использование сервера распознавания с Asterisk

### Устанавливаем зависимости

 - asterisk
 - docker
 - пакеты для работы со звуком: 

        sudo apt install sox espeak

 - пакет для python AGI и вебсокетов

        sudo pip3 install pyst2 websocket-client

### Запускаем сервер распознавания

docker run -d -p 2700:2700 alphacep/kaldi-ru:latest

### Проверяем, что можем запустить EAGI скрипт 

Код скрипта находится в файле [eagi-ru.py](https://github.com/alphacep/api-samples/blob/master/asterisk/eagi-ru.py) из этого пакета:

```
cd /home/user
git clone https://github.com/alphacep/api-samples
cd api-samples/asterisk
python3 eagi-ru.py
ARGS: ['eagi-ru.py']
^C
```

### Настраиваем план звонков

В etc/extensions.conf

```
exten => 200,1,Answer()
same = n,EAGI(/home/user/api-samples/asterisk/eagi-ru.py)
same = n,Hangup()
```

### Звоним и проверяем работу

Для написания чатбота, сохранения результатов в базу, и так далее,
изменяем код eagi-ru.py.

