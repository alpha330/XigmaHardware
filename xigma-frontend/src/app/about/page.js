// src/app/about/page.js
import AboutClient from '../../components/website/AboutClient';

// کش کردن صفحه درباره ما (چون محتوای آن به ندرت تغییر می‌کند)
export const revalidate = 3600; // هر یک ساعت یک‌بار آپدیت شود

async function getAboutPageData() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/website/pages/about/', {
      next: { revalidate: 3600 }
    });

    if (!res.ok) throw new Error('Failed to fetch about page');

    return await res.json();
  } catch (error) {
    console.error('About page fetch error:', error);

    // دیتای تستی (Mock) در صورتی که بک‌اند متصل نباشد یا ارور بدهد
    return {
      title: "درباره ما",
      content: `
        <h2>تخصص ما، پیشرفت شماست</h2>
        <p>مجموعه <strong>XigmaHardware</strong> با بیش از یک دهه تجربه در زمینه واردات و توزیع تجهیزات تخصصی شبکه، سرورهای سازمانی، قطعات ورک‌استیشن و سیستم‌های پردازش سنگین، همواره در تلاش بوده تا بهترین زیرساخت‌های فناوری اطلاعات را برای کسب‌وکارها و متخصصین فراهم کند.</p>

        <h3>ماموریت ما</h3>
        <p>ما معتقدیم که قلب تپنده هر سازمان موفق، زیرساخت فناوری اطلاعات آن است. ماموریت ما ارائه راهکارهای سخت‌افزاری پایدار، ایمن و مقیاس‌پذیر با منصفانه‌ترین قیمت ممکن است.</p>

        <h3>چرا زیگما سخت‌افزار؟</h3>
        <ul>
          <li>تامین مستقیم کالا از تولیدکنندگان معتبر جهانی</li>
          <li>تست و بررسی دقیق قطعات پیش از ارسال در لابراتوارهای تخصصی</li>
          <li>مشاوره رایگان برای کانفیگ سرورها و ورک‌استیشن‌ها بر اساس نیاز دقیق مشتری</li>
          <li>پشتیبانی نرم‌افزاری و سخت‌افزاری پس از فروش</li>
        </ul>
      `
    };
  }
}

// اضافه کردن متادیتای سئو برای صفحه درباره ما
export const metadata = {
  title: 'درباره ما | XigmaHardware',
  description: 'آشنایی با تاریخچه، ماموریت و خدمات مجموعه XigmaHardware، تامین‌کننده تخصصی تجهیزات شبکه و کامپیوتر.',
};

export default async function AboutPage() {
  const pageData = await getAboutPageData();

  return <AboutClient pageData={pageData} />;
}