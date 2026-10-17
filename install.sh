#!/usr/bin/env bash
# Установка VK iOS Notifications на сервер (Ubuntu/Debian и др. Linux с systemd).
# Запуск: curl -fsSL <ссылка на этот файл> | sudo bash
set -euo pipefail

REPO_URL="https://github.com/Zarrock1/vk-ios-notifications.git"
INSTALL_DIR="${INSTALL_DIR:-/opt/vk-ios-notifications}"

info() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31mОшибка:\033[0m %s\n' "$*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || fail "запустите от root: curl -fsSL ... | sudo bash"

if ! command -v git >/dev/null 2>&1; then
    info "Устанавливаю git"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y -qq git
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y -q git
    else
        fail "установите git вручную"
    fi
fi

if ! command -v docker >/dev/null 2>&1; then
    info "Устанавливаю Docker"
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker >/dev/null 2>&1 || true
docker compose version >/dev/null 2>&1 || fail "нет плагина docker compose — обновите Docker"

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Обновляю $INSTALL_DIR"
    git -C "$INSTALL_DIR" pull --ff-only
else
    info "Скачиваю проект в $INSTALL_DIR"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
cd "$INSTALL_DIR"

if [ ! -f .env ]; then
    # При запуске через "curl | bash" stdin занят скриптом — читаем с терминала
    [ -r /dev/tty ] || fail "нет терминала для ввода токенов: создайте $INSTALL_DIR/.env по образцу sample.env"
    echo
    echo "Токен VK: инструкция — https://github.com/Zarrock1/vk-ios-notifications#как-получить-токен-vk"
    read -r -s -p "VK_TOKEN или вся адресная строка после входа (ввод скрыт): " vk_token < /dev/tty; echo
    echo "Получено символов: ${#vk_token}"
    read -r -p "Ключ Bark или ссылка из приложения (https://api.day.app/...): " bark_token < /dev/tty
    [ -n "$vk_token" ] && [ -n "$bark_token" ] || fail "токены не могут быть пустыми"
    umask 077
    cat > .env <<EOF
VK_TOKEN=$vk_token
BARK_TOKEN=$bark_token
EOF
    info "Настройки сохранены в $INSTALL_DIR/.env"
fi

info "Собираю образ"
docker compose build -q

info "Проверяю токены (на iPhone должно прийти тестовое уведомление)"
if ! docker compose run --rm -T vk-notifications python -m src.main check; then
    fail "проверка не прошла — исправьте $INSTALL_DIR/.env (nano $INSTALL_DIR/.env) и запустите скрипт снова"
fi

info "Запускаю сервис"
docker compose up -d
sleep 5
docker compose logs --tail 20 vk-notifications

echo
info "Готово! Сервис запущен и сам стартует после перезагрузки сервера."
echo "  Логи:        cd $INSTALL_DIR && docker compose logs -f"
echo "  Перезапуск:  cd $INSTALL_DIR && docker compose restart"
echo "  Обновление:  запустите этот скрипт ещё раз"
