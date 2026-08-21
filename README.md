# XigmaHardware

فروشگاه آنلاین تجهیزات کامپیوتر، سرور و ورک‌استیشن با Backend مبتنی بر Django و Frontend مبتنی بر Next.js.

## معماری

- `emarket-backend/`: Django 5، Django REST Framework، Celery
- `xigma-frontend/`: Next.js 16، React 19
- PostgreSQL 16 برای داده‌های اصلی
- Redis 7 برای Cache و صف Celery
- Nginx برای ورودی یکپارچه‌ی Frontend و API
- `docker-compose.*.yml`: محیط‌های development، test، staging و production

## راه‌اندازی Development

پیش‌نیازها: Docker Compose، Node.js 22 و npm.

```bash
cp .env.example .env
make dev-build
```

Backend و سرویس‌های وابسته با Docker اجرا می‌شوند. Frontend را در ترمینال دیگری اجرا کنید:

```bash
cd xigma-frontend
cp .env.example .env.local
npm ci
npm run dev
```

آدرس‌های Development:

- Frontend: `http://localhost:3000`
- API و Swagger: `http://localhost:8000/swagger/`
- MailHog: `http://localhost:8025`
- Flower: با profile ابزارها و از طریق `make dev-tools`

هیچ حساب کاربری یا رمز عبور پیش‌فرضی داخل مخزن تعریف نشده است. برای ساخت مدیر:

```bash
make superuser
```

## داده‌های نمونه‌ی انبار

برای ایجاد یا به‌روزرسانی کاتالوگ نمونه در محیط Development اجرا کنید:

```bash
make seed-stock
```

این فرمان ۴ شاخه‌ی اصلی دیتاسنتر، سازمانی/اداری، خانگی و ورک‌استیشن را همراه با زیرشاخه‌ها، برندها، سری‌ها و محصولات نمونه می‌سازد. اجرای مجدد آن رکورد تکراری ایجاد نمی‌کند. محصولات با قیمت آزمایشی و وضعیت پیش‌نویس ساخته می‌شوند و در مارکت قابل مشاهده نیستند.

فرمان‌های مستقل و حالت آزمایشی نیز در دسترس‌اند:

```bash
python manage.py seed_stock_categories
python manage.py seed_stock_brands
python manage.py seed_stock_products
python manage.py seed_stock_sample --dry-run
```

## تست و کنترل کیفیت

Backend:

```bash
cd emarket-backend
python -m pip install -r requirements/test.txt
pytest -q
```

Frontend:

```bash
cd xigma-frontend
npm ci
npm run lint
npm run build
npm audit --omit=dev --audit-level=high
```

اجرای تست Backend در Docker:

```bash
make test-docker
```

همین کنترل‌ها در `.github/workflows/ci.yml` برای push به `main` و Pull Request اجرا می‌شوند.

## Staging و Production

ابتدا `.env.example` را کپی و تمام placeholderها را با مقادیر امن جایگزین کنید. سپس:

```bash
make stage
# یا
make prod
```

در Production، `NEXT_PUBLIC_API_URL` خالی می‌ماند تا مرورگر API را به‌صورت same-origin از Nginx دریافت کند. متغیر `API_URL` در کانتینر Frontend به Backend داخلی اشاره می‌کند.

برای PostgreSQL داخلی، `DB_SSLMODE=prefer` مناسب است. هنگام اتصال به دیتابیس خارجی دارای TLS آن را به `require` یا ترجیحاً `verify-full` تغییر دهید.

در production باید TLS روی load balancer یا reverse proxy جلویی terminate شود و هدر `X-Forwarded-Proto` حفظ شود. تنظیمات staging به‌صورت پیش‌فرض HTTP است؛ در صورت فعال‌کردن TLS، متغیرهای `SECURE_SSL_REDIRECT` و `SECURE_COOKIES` را نیز فعال کنید.

## نکات امنیتی

- `SECRET_KEY`، رمزهای PostgreSQL/Redis، اطلاعات SMTP و کلیدهای سرویس‌ها نباید commit شوند.
- `NESHAN_API_KEY` فقط در محیط Server قرار می‌گیرد و از Route Handler داخلی Next.js استفاده می‌شود.
- کلید Neshan که قبلاً در کد Client قرار گرفته بود باید در پنل ارائه‌دهنده rotate شود؛ حذف آن از آخرین نسخه، تاریخچه‌ی Git را باطل نمی‌کند.
- پرداخت زرین‌پال از اعتبارسنجی پیش‌فرض TLS استفاده می‌کند؛ غیرفعال‌کردن certificate verification ممنوع است.
- commit و push مستقیم از Makefile حذف شده‌اند. توسعه باید روی feature branch و از طریق Pull Request انجام شود.

## وضعیت فعلی

پایه‌ی فنی، build و تست‌های موجود تثبیت شده‌اند. تکمیل پوشش تست سایر domainها و جریان کامل سفارش تا ارسال، در فازهای بعدی پروژه انجام می‌شود.
