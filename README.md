# Marketplace Backend

مارکت‌پلیس آنلاین - بک‌اند Django REST Framework

## 🏗️ ساختار پروژه
emarket-backend/ # کد اصلی بک‌اند
├── config/ # تنظیمات Django
├── apps/ # اپلیکیشن‌ها
│ ├── accounts/ # مدیریت کاربران ✅
│ ├── market/ # بازار
│ ├── stock/ # انبار
│ ├── financial/ # مالی
│ ├── payment/ # پرداخت
│ └── basket/ # سبد خرید
├── requirements/ # پکیج‌های Python
└── docker/ # تنظیمات Docker


## 🚀 راه‌اندازی سریع

### Development
```bash
make dev-build

آدرس‌ها
API: http://localhost:8000/swagger/

MailHog: http://localhost:8025/

Flower: http://localhost:5555/

حساب‌های تست

Admin: admin@example.com / Admin123!@#
User:  user1@example.com / TestPass123!

make help          # نمایش همه دستورات
make dev           # اجرای محیط توسعه
make test          # اجرای تست‌ها
make shell         # Django shell
make migrate       # اجرای migrations
make create-dev-data  # ایجاد داده‌های تست

🛠️ تکنولوژی‌ها
Backend: Django 5.0 + Django REST Framework

Database: PostgreSQL 16

Cache: Redis 7

Async: Celery + Redis

Email Dev: MailHog

Documentation: Swagger/ReDoc


## 🎯 **تفکیک مسئولیت‌ها**

### سطح روت (XigmaMarket/XigmaHardware/)
- `docker-compose.*.yml` - مدیریت همه سرویس‌ها
- `.env.*` - متغیرهای محیطی همه سرویس‌ها
- `Makefile` - دستورات مدیریت کل پروژه
- `README.md` - مستندات اصلی

### سطح بک‌اند (emarket-backend/)
- `Dockerfile.*` - نحوه ساخت ایمیج بک‌اند
- `manage.py` - Django CLI
- `config/` - تنظیمات Django
- `apps/` - کد اصلی
- `requirements/` - پکیج‌های Python
- `docker/` - اسکریپت‌های Docker

## 🚀 **اجرای پروژه**

```bash
# از سطح روت پروژه:
cd XigmaMarket/XigmaHardware

# اجرای توسعه
make dev

# یا مستقیم با docker-compose
docker-compose -f docker-compose.dev.yml up -d

# مشاهده وضعیت
docker-compose -f docker-compose.dev.yml ps

# توقف
make dev-down