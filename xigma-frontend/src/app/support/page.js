// src/app/support/page.js
import SupportClient from '../../components/support/SupportClient';

export const revalidate = 3600; // کش کردن صفحه برای یک ساعت

const normalizeData = (data) => {
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

async function getFaqs() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/support/faqs/', {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error();
    return normalizeData(await res.json());
  } catch (error) {
    // داده‌های Mock (آفلاین) برای تست
    return [
      {
        id: 1,
        question: 'چگونه می‌توانم از گارانتی محصول استفاده کنم؟',
        answer: 'برای استفاده از خدمات گارانتی، دستگاه باید به همراه جعبه اصلی و فاکتور خرید به مرکز خدمات زیگما ارسال شود. برای هماهنگی ابتدا یک تیکت در بخش پشتیبانی ثبت کنید.'
      },
      {
        id: 2,
        question: 'شرایط مرجوعی کالا در XigmaHardware چیست؟',
        answer: 'شما تا ۷ روز پس از دریافت کالا، در صورت عدم مغایرت پلمپ و سخت‌افزار، می‌توانید محصول را مرجوع کنید. قطعات سرور در صورت باز شدن پلمپ به هیچ وجه قابل مرجوعی نیستند.'
      },
      {
        id: 3,
        question: 'آیا امکان اسمبل قطعات و کانفیگ سرور پیش از ارسال وجود دارد؟',
        answer: 'بله. متخصصین ما در لابراتوار زیگما می‌توانند سرور یا ورک‌استیشن شما را بر اساس نیازتان کاملا اسمبل، تست و سپس ارسال کنند.'
      },
      {
        id: 4,
        question: 'چه مدت طول می‌کشد تا سفارش به دستم برسد؟',
        answer: 'سفارشات شهر تهران در کمتر از ۲۴ ساعت و شهرستان‌ها از طریق باربری و تیپاکس بین ۲ الی ۳ روز کاری زمان می‌برد.'
      }
    ];
  }
}

export const metadata = {
  title: 'پشتیبانی و خدمات پس از فروش | XigmaHardware',
  description: 'مرکز پشتیبانی زیگما سخت‌افزار. استعلام گارانتی قطعات، ثبت تیکت پشتیبانی و سوالات متداول مشتریان.',
};

export default async function SupportPage() {
  const faqs = await getFaqs();

  return <SupportClient faqs={faqs} />;
}