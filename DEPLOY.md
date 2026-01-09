# Инструкция по развертыванию проекта

## Railway.app (Рекомендуется)

### Шаг 1: Подготовка проекта

1. Убедитесь, что все изменения закоммичены в Git:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. Создайте файл `Procfile` в корне проекта:
```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn settings.wsgi:application
```

3. Обновите `requirements.txt`, добавив:
```
gunicorn==21.2.0
whitenoise==6.6.0
```

### Шаг 2: Настройка Railway

1. Зарегистрируйтесь на https://railway.app
2. Нажмите "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически определит Django проект

### Шаг 3: Настройка переменных окружения

В Railway Dashboard → Variables добавьте:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
STRIPE_SECRET_KEY=sk_live_your_key
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY_KZT=sk_live_your_kzt_key
STRIPE_PUBLIC_KEY_KZT=pk_live_your_kzt_key
```

### Шаг 4: Настройка базы данных

1. В Railway Dashboard → New → Database → PostgreSQL
2. Railway автоматически создаст переменную `DATABASE_URL`
3. Обновите `settings/base.py` для использования PostgreSQL:

```python
import dj_database_url

# В конце файла settings/base.py добавьте:
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(
        os.environ.get('DATABASE_URL')
    )
```

4. Добавьте в `requirements.txt`:
```
dj-database-url==2.1.0
psycopg2-binary==2.9.9
```

### Шаг 5: Настройка статических файлов

1. Добавьте в `settings/base.py`:
```python
# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise для статических файлов
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Шаг 6: Деплой

1. Railway автоматически задеплоит проект
2. После деплоя выполните миграции:
   - В Railway Dashboard → Deployments → View Logs
   - Или через Railway CLI: `railway run python manage.py migrate`

3. Создайте суперпользователя:
   - `railway run python manage.py createsuperuser`

### Шаг 7: Получение URL

1. В Railway Dashboard → Settings → Domains
2. Railway предоставит URL вида: `your-project.railway.app`
3. Можно добавить свой домен

## Render.com (Альтернатива)

### Шаг 1: Подготовка

1. Создайте `render.yaml` в корне проекта:
```yaml
services:
  - type: web
    name: stripe-django
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn settings.wsgi:application
    envVars:
      - key: SECRET_KEY
        sync: false
      - key: DEBUG
        value: False
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_PUBLIC_KEY
        sync: false
```

2. Зарегистрируйтесь на https://render.com
3. New → Web Service → Connect GitHub
4. Выберите репозиторий
5. Настройте переменные окружения
6. Deploy!

## Важные моменты

1. **SECRET_KEY**: Используйте сильный секретный ключ для продакшена
2. **DEBUG**: Всегда `False` в продакшене
3. **ALLOWED_HOSTS**: Обновите в `settings/base.py`:
   ```python
   ALLOWED_HOSTS = ['your-domain.railway.app', 'your-domain.com']
   ```
4. **Stripe Keys**: Используйте live ключи для продакшена
5. **База данных**: Используйте PostgreSQL вместо SQLite
6. **Статические файлы**: Настройте WhiteNoise или CDN

## Проверка после деплоя

1. Проверьте главную страницу: `https://your-domain.railway.app/`
2. Проверьте админку: `https://your-domain.railway.app/admin/`
3. Проверьте оплату товара: `https://your-domain.railway.app/item/1/`
4. Проверьте корзину: `https://your-domain.railway.app/orders/cart/`

## Обновление requirements.txt

Убедитесь, что в `requirements.txt` есть:
```
Django==6.0.1
stripe==14.1.0
python-decouple==3.8
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
psycopg2-binary==2.9.9
pillow==12.1.0
```

