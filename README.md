# Социальная сеть для любителей кулинарии

Сайт является площадкой, где можно выкладывать свои рецепты, смотреть рецепты других пользователей, добавлять особо полюбившиеся рецепты и авторов в избранное.

Приложение автоматически посчитает что и в каком количестве необходимо купить для ваших любимых рецептов. Список покупок можно скачать отдельным файлом.

### Адрес сервера
```
84.201.153.159
```

## Порядок запуска


### Установить соединение с сервером по протоколу ssh:

```
ssh your_username@84.201.153.159
```

username - имя пользователя, под которым будет выполнено подключение к серверу
server_address - IP-адрес сервера 

### Запустить docker-compose со всеми контейнерами

```
sudo docker-compose up -d --build
```

### Отключение docker-compose

```
sudo docker-compose down
```