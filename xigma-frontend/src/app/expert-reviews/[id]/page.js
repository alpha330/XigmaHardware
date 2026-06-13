// src/app/expert-reviews/[id]/page.js
import ExpertReviewDetailClient from '../../../components/website/ExpertReviewDetailClient';

async function getExpertReviewDetail(id) {
  try {
    const res = await fetch(`http://localhost:8000/api/v1/website/articles/${id}/`, { cache: 'no-store' });
    if (!res.ok) throw new Error();
    return await res.json();
  } catch (error) {
    return {
      id,
      title: 'بررسی تخصصی سرور HP DL380 G10 در لابراتوار زیگما',
      expert_score: 9.5,
      content: `
        <h2>معرفی اولیه</h2>
        <p>سرورهای نسل دهم اچ‌پی بدون شک یکی از پرفروش‌ترین‌ها در دیتاسنترهای خاورمیانه هستند. ما در لابراتوار زیگما سخت‌افزار این سرور را با پردازنده‌های Gold زیر تست‌های سنگین مجازی‌سازی قرار دادیم.</p>
        <h2>بنچمارک‌ها و نتایج حرارتی</h2>
        <p>در طول ۴۸ ساعت پردازش مداوم، دمای سیستم از حد استاندارد تجاوز نکرد و فن‌ها عملکرد هوشمندی از خود نشان دادند.</p>
        <h2>جمع‌بندی</h2>
        <p>اگر به دنبال یک بستر امن و مقیاس‌پذیر هستید، این کانفیگ تمام نیازهای شما را تا ۵ سال آینده تضمین می‌کند.</p>
      `,
      pros: ['پشتیبانی از پردازنده‌های قدرتمند', 'مدیریت حرفه‌ای iLO 5', 'قابلیت ارتقا بالا'],
      cons: ['هزینه بالای قطعات اورجینال در بازار', 'وزن بالا برای جابجایی']
    };
  }
}

export default async function ExpertReviewDetailPage({ params }) {
  const resolvedParams = await params;
  const review = await getExpertReviewDetail(resolvedParams.id);

  return <ExpertReviewDetailClient review={review} />;
}