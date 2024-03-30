# GitHub API Parser + API application #

## Требования ##
1. [Python >= 3.10](https://www.python.org/downloads/)
2. [Poetry](https://pypi.org/project/poetry/)

---

## 1.API application ##
### Запуск проекта через Docker ###
`docker compose -f 'deploy/docker-compose.yml' up -d'`

### Классический метод запуска проекта ###
1. Вход в виртуальное окружение:
    `
    poetry shell 
    `
2. Установка зависимостей:
    `
    poetry install
    `
3. Поднятие PostgreSQL с помощью Docker:
    `
    docker compose -f 'docker-compose.dev.yml' up -d
    `
4. Выполнение миграций:
    `
    alembic updrage head
    `
5. Инициализация линтера:
    `
    pre-commit install
    `
6. Запуск тестов:
    `
    pytest
    `
7. Запуск сервера для разработки на http://localhost:8000:
    `
    uvicorn main:app --reload
    `

---

## 2.GitHub API parser ##
### Запуск функции и триггера в Yandex Cloud ###
1. Убедиться, что определены следующие переменные окружения:
   * `$FOLDER_ID` - если не определен, 
   то выполнить команду в терминале: `yc resource-manager folder list` и 
   в выведенной таблице выбрать значение из столбца `id`. В случае отсутствия в выводе какого-либо `id`, выполнить такую команду:
   `
   yc resource-manager folder create \
   --name <new-folder>
   `
   * `$SERVICE_ACCOUNT_ID` - если не определен, 
   то выполнить команду в терминале: `yc iam service-account list` и
   аналогично выбрать значение. В случае отсутствия в выводе какого-либо `id`, выполнить такую команду:
   `
   yc iam service-account create \
   --name <service-account> \
   --description 'Github API parsing service account' \
   --format json
   `.
   * `$DB_NAME` - название базы данных (не СУБД).
   * `$DB_USER` - пользователь базы данных, от имени которого будет осуществлен доступ.
   * `$DB_PASSWORD` - пароль пользователя.
   * `$DB_HOST` - имя хоста, на котором размещена СУБД.
   * `$DB_PORT` - номер порта, подключения к которому прослушиваются СУБД.
2. [Опционально] Создать или использовать уже готовый персональный токен GitHub для увеличения лимита запросов в час.
    Сохранить его значение в переменную окружения `$GITHUB_TOKEN`.
3. Запустить скрипт `yandex-cloud-function.sh`:
    `sh yandex-cloud-function.sh`, выполняющий следующие действия:
   1. Назначает роль `editor` сервисному аккаунту с `id`=`$SERVICE_ACCOUNT_ID`
      для обеспечения доступа к дальнейшим операциям.
   2. Определяет облачную функцию с именем `github-api-parser`.
   3. Запаковывает в архив `github_api_parser.zip` содержимое папки `scheduled_parser`.
   4. Создает новую версию облачной функции с необходимыми параметрами.
   5. Создает триггер для созданной функции, запускающий ее каждый час. Такой интервал
      обусловлен наличием лимита у GitHub API на количество запросов в час: 60 для не аутентифицированных 
      и 5000 для аутентифицированных.

---

## Обозначения символов в коммитах ##
- `+` - добавлено
- `-` - удалено
- `=` - изменено/улучшено
- `!` - исправлено