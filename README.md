# Django + Stripe API Backend

Простой Django сервер с интеграцией Stripe для обработки платежей за товары.

## Описание

Проект реализует Django бэкенд с интеграцией Stripe API для создания платежных форм и обработки платежей. Поддерживается работа с разными валютами (USD, KZT) с использованием разных Stripe ключей.

## Функционал

### Основные возможности:

- ✅ Django модель `Item` с полями (name, description, price, currency)
- ✅ API `GET /buy/{id}` - получение Stripe Session Id для оплаты товара
- ✅ API `GET /item/{id}` - HTML страница с информацией о товаре и кнопкой Buy
- ✅ Модель `Order` для объединения нескольких товаров
- ✅ Модели `Discount` и `Tax` для применения скидок и налогов к заказам
- ✅ Поддержка разных валют (USD, KZT) с разными Stripe ключами
- ✅ Django Admin панель для управления моделями
- ✅ Payment Intent endpoint и полноценная форма оплаты (бонусная задача)

### Бонусные возможности:

- ✅ Docker поддержка
- ✅ Использование environment variables
- ✅ Улучшенная Django Admin панель
- ✅ Payment Intent вместо Session

## Установка и запуск

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd test_task_ooo_rishat
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Создайте файл `.env` на основе `env.example`:
```bash
cp env.example .env
```

6. Заполните переменные окружения в `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=*

# Stripe Keys - USD (default)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_usd
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key_usd

# Stripe Keys - KZT (optional, will use USD keys if not provided)
STRIPE_SECRET_KEY_KZT=sk_test_your_stripe_secret_key_kzt
STRIPE_PUBLIC_KEY_KZT=pk_test_your_stripe_public_key_kzt

# Database Configuration (PostgreSQL)
# Если не указаны, будет использоваться SQLite
DB_NAME=stripe_db
DB_USER=stripe_user
DB_PASSWORD=stripe_password
DB_HOST=localhost
DB_PORT=5432
```

**Примечание:** Если вы не настроите PostgreSQL, проект будет использовать SQLite для локальной разработки.

7. (Опционально) Настройте PostgreSQL:
   - Установите PostgreSQL на вашей системе
   - Создайте базу данных:
   ```bash
   createdb stripe_db
   ```
   - Убедитесь, что в `.env` указаны настройки PostgreSQL (см. выше)
   - Если PostgreSQL не настроен, будет использоваться SQLite

8. Выполните миграции:
```bash
python manage.py migrate
```

9. Создайте суперпользователя для доступа к админке:
```bash
python manage.py createsuperuser
```

10. Запустите сервер:
```bash
python manage.py runserver
```

11. Откройте в браузере:
- Главная страница: http://127.0.0.1:8000/
- Админ панель: http://127.0.0.1:8000/admin/

### Запуск с Docker

1. Создайте файл `.env` (см. выше)

2. Соберите и запустите контейнеры (включая PostgreSQL):
```bash
docker-compose up --build
```

3. Миграции выполнятся автоматически при запуске. Если нужно выполнить вручную:
```bash
docker-compose exec web python manage.py migrate
```

4. Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Откройте в браузере:
- Главная страница: http://localhost:8000/
- Админ панель: http://localhost:8000/admin/

**Примечание:** Docker Compose автоматически настроит PostgreSQL. База данных будет сохранена в volume `postgres_data`.

## API Endpoints

### Товары

- `GET /` - главная страница со списком товаров
- `GET /item/{id}/` - страница товара с кнопкой Buy
- `GET /item/{id}/pay/` - страница товара с формой оплаты через Payment Intent
- `GET /buy/{id}/` - получение Stripe Session Id для оплаты товара
- `GET /payment-intent/{id}/` - создание Payment Intent для товара (бонус)
- `GET /success/` - страница успешной оплаты
- `GET /cancel/` - страница отмены оплаты

### Заказы

- `GET /orders/cart/` - корзина покупок
- `GET /orders/order/{id}/` - страница заказа
- `GET /orders/buy-order/{id}/` - получение Stripe Session Id для оплаты заказа
- `POST /orders/add-to-cart/{item_id}/` - добавление товара в корзину
- `POST /orders/remove/{item_id}/` - удаление товара из корзины
- `POST /orders/decrease/{item_id}/` - уменьшение количества товара в корзине

## Использование

### Пример запроса для получения Session Id:

```bash
curl -X GET http://localhost:8000/buy/1/
```

Ответ:
```json
{
  "id": "cs_test_..."
}
```

### Пример HTML страницы товара:

```bash
curl -X GET http://localhost:8000/item/1/
```

## Структура проекта

```
test_task_ooo_rishat/
├── apps/
│   ├── abstracts/      # Абстрактные модели
│   ├── items/          # Модели и views для товаров
│   └── orders/         # Модели и views для заказов
├── settings/           # Настройки Django
├── media/              # Медиа файлы (изображения товаров)
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── env.example
└── README.md
```

## Модели

### Item
- `name` - название товара
- `description` - описание товара
- `price` - цена в центах
- `currency` - валюта (USD, KZT)
- `image` - изображение товара

### Order
- `is_paid` - статус оплаты
- `discount` - скидка (ForeignKey к Discount)
- `tax` - налог (ForeignKey к Tax)
- Методы: `subtotal()`, `total_amount()`

### OrderItem
- `order` - заказ (ForeignKey к Order)
- `item` - товар (ForeignKey к Item)
- `quantity` - количество

### Discount
- `name` - название скидки
- `code` - промокод
- `percent` - процент скидки

### Tax
- `name` - название налога
- `percent` - процент налога

## Настройка Stripe

1. Зарегистрируйтесь на [Stripe](https://stripe.com)
2. Получите тестовые ключи в [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
3. Добавьте ключи в файл `.env`

Для поддержки разных валют создайте отдельные Stripe аккаунты или используйте разные ключи для разных валют.

## Тестирование

Для тестирования используйте тестовые карты Stripe:
- Успешная оплата: `4242 4242 4242 4242`
- Отклоненная карта: `4000 0000 0000 0002`
- Требует 3D Secure: `4000 0025 0000 3155`

Подробнее: https://stripe.com/docs/testing

## Payment Intent vs Checkout Session

Проект поддерживает два способа оплаты:

### Checkout Session (по умолчанию)
- **URL**: `/item/{id}/` → кнопка "Оплатить через Checkout Session"
- **Как работает**: Пользователь перенаправляется на страницу Stripe
- **Преимущества**:
  - Простая реализация
  - Stripe обрабатывает весь UI
  - Автоматическая обработка ошибок
- **Недостатки**:
  - Пользователь покидает ваш сайт
  - Ограниченная кастомизация

### Payment Intent (бонусная задача)
- **URL**: `/item/{id}/pay/` → кнопка "Оплатить через Payment Intent (на сайте)"
- **Как работает**: Оплата происходит прямо на вашем сайте
- **Преимущества**:
  - Пользователь остается на сайте
  - Полный контроль над UI
  - Гибкая кастомизация формы оплаты
  - Можно сохранять карты для будущих платежей
- **Недостатки**:
  - Более сложная реализация
  - Нужно создавать свой UI для оплаты

### Как протестировать Payment Intent:

1. Перейдите на страницу товара: `http://localhost:8000/item/1/`
2. Нажмите кнопку **"Оплатить через Payment Intent (на сайте)"**
3. Заполните форму:
   - Данные карты (автоматически создается через Stripe Elements)
   - Имя держателя карты
   - Email
4. Нажмите "Оплатить"
5. Оплата произойдет без перенаправления на Stripe

## Развертывание

Для развертывания на продакшене:

1. Измените `DEBUG=False` в `.env`
2. Настройте `ALLOWED_HOSTS` в `settings/base.py`
3. Используйте продакшн ключи Stripe
4. Настройте статические файлы (например, через nginx)
5. Используйте PostgreSQL вместо SQLite для продакшена

## Лицензия

Этот проект создан в рамках тестового задания.

