# VK iOS Notifications

Пересылает новые сообщения ВКонтакте в push-уведомления на iOS через [Bark](https://github.com/Finb/Bark).
В уведомлении: имя отправителя (заголовок), текст сообщения и его аватарка.

## Как это работает

Сервис слушает события через [VK Long Poll API](https://dev.vk.com/ru/api/user-long-poll/getting-started).
При новом входящем сообщении он запрашивает данные отправителя (имя и фото — для бесед
определяется настоящий автор, а не чат) и отправляет уведомление на устройство через Bark.

- Исходящие сообщения игнорируются.
- Диалоги с отключёнными уведомлениями пропускаются.
- Данные отправителей кэшируются, чтобы не дёргать VK API на каждое сообщение.
- При сетевых сбоях и ошибках VK API сервис автоматически переподключается
  с экспоненциальной задержкой (5 с → 10 с → … → максимум 5 минут).
- Обработка сообщений идёт в отдельных потоках — пачка сообщений не тормозит Long Poll.
- Уведомления группируются по диалогам, в беседах в заголовке видно название беседы.
- Если токен VK умер или не подходит, сервис **присылает об этом push** и раз в 30 минут
  проверяет токен снова (контейнер не перезапускается по кругу). Когда токен заработает, придёт push.
- Отправка в Bark идёт POST-запросом (длинные тексты и спецсимволы не ломают URL), с повторами при сбоях.

## Почему уведомления могли не работать

Чаще всего дело в **токене VK**:

| Симптом в логах | Причина |
|---|---|
| `[5] User authorization failed` / `[1117]` | токен просрочен: его выдали без права `offline` (живёт 24 ч) или отозвали |
| `[15] Access denied` / `[7]` | токен выдан приложением без доступа к сообщениям (ВК пускает к ним не все приложения) |
| `[27] Group authorization failed` | это токен сообщества, а нужен токен **пользователя** |
| `Bark вернул ошибку: 400 ... device token` | неверный `BARK_TOKEN` или ключ от другого сервера Bark |

Быстро всё проверить: `docker compose run --rm vk-notifications python -m src.main check`.
Команда проверит токен VK и пришлёт тестовый push.

## Как получить токен VK

1. Откройте в браузере (вы должны быть залогинены в VK):

   ```
   https://oauth.vk.com/authorize?client_id=2685278&scope=messages,offline&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1
   ```

   `2685278` — приложение Kate Mobile, у него есть доступ к сообщениям.
2. Разрешите доступ. Откроется пустая страница — скопируйте из адресной строки значение
   `access_token=` (от `vk1.a.` до `&expires_in`). При `expires_in=0` токен бессрочный.
3. Вставьте его в `.env` как `VK_TOKEN`.

> Токен даёт полный доступ к вашим сообщениям — никому его не передавайте.
> Если вы сменили пароль или нажали «Завершить все сеансы», токен перестанет работать — получите новый.

## Требования

- Токен VK пользователя с правами `messages,offline` (см. выше).
- Ключ устройства Bark: установите [приложение Bark](https://apps.apple.com/app/bark-custom-notifications/id1403753865)
  на iPhone — ключ показан на главном экране приложения (можно скопировать ссылку целиком).

## Конфигурация

Создайте файл `.env` в корне проекта (пример — в [sample.env](sample.env)):

```env
VK_TOKEN=vk1.a.xxxxxxxx
BARK_TOKEN=xxxxxxxx
```

| Переменная | По умолчанию | Описание |
|---|---|---|
| `VK_TOKEN` | — | токен пользователя VK |
| `BARK_TOKEN` | — | ключ устройства Bark или ссылка `https://api.day.app/KEY/` |
| `BARK_URL` | `https://api.day.app` | адрес сервера Bark |
| `BARK_SOUND` | — | звук уведомления (названия — в приложении Bark) |
| `BARK_LEVEL` | — | `active`, `timeSensitive` (пробивает «Фокус»), `passive`, `critical` |
| `BARK_GROUP_BY_DIALOG` | `true` | группировать уведомления по диалогам |
| `READ_CHECK_DELAY` | `2` | через сколько секунд проверить, не прочитано ли сообщение на другом устройстве; `0` — не проверять |
| `NOTIFY_STARTUP` | `true` | присылать push при запуске сервиса |

## Установка на сервер (Docker Compose)

Подойдёт любой VPS с Linux и установленным Docker.

```bash
git clone https://github.com/Zarrock1/vk-ios-notifications.git
cd vk-ios-notifications
cp sample.env .env
nano .env                                   # впишите VK_TOKEN и BARK_TOKEN

docker compose run --rm vk-notifications python -m src.main check   # проверка
docker compose up -d --build                # запуск в фоне, стартует вместе с сервером
docker compose logs -f                      # логи
```

Обновление: `git pull && docker compose up -d --build`.

### Свой сервер Bark (по желанию)

По умолчанию push идут через публичный `api.day.app`, то есть текст сообщений проходит через чужой сервер.
Свой сервер Bark поднимается вместе с сервисом:

```bash
docker compose --profile bark up -d --build
```

Дальше в приложении Bark на iPhone: «Серверы» → «+» → `http://<IP сервера>:8080`
(лучше за HTTPS-прокси, например Caddy). Ключ, который покажет приложение для этого сервера,
впишите в `BARK_TOKEN`, а в `.env` укажите `BARK_URL=http://bark-server:8080`,
затем выполните `docker compose up -d`.

## Запуск локально

Требуется Python 3.13+ и [Poetry](https://python-poetry.org/):

```bash
poetry install --no-root
poetry run python -m src.main check   # проверка токенов
poetry run python -m src.main
```

## Запуск в Docker без Compose

```bash
docker build -t vk-ios-notifications .
docker run -d --name vk-ios-notifications --restart unless-stopped --env-file .env vk-ios-notifications
```

Файл `.env` не копируется в образ (см. [.dockerignore](.dockerignore)) —
токены передаются только через `--env-file` или `-e`.

Готовый образ собирается автоматически при пуше в `main`/`develop`
(см. [build_app.yml](.github/workflows/build_app.yml)) и публикуется в GitHub Container Registry:

```bash
docker run -d --restart unless-stopped --env-file .env ghcr.io/zarrock1/vk-ios-notifications:main
```

## Структура проекта

```
src/
├── main.py              # точка входа, команда check
├── core/
│   ├── vk.py            # слушатель Long Poll VK, реконнект, алерты о токене
│   ├── exceptions.py    # ошибки
│   └── bark.py          # отправка push-уведомлений через Bark
└── settings/
    ├── config.py        # настройки из .env (pydantic-settings)
    └── constants.py     # константы (иконка VK по умолчанию)
```
