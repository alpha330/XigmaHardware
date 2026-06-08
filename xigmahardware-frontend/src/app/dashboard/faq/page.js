// src/app/dashboard/faq/page.js
import { getFAQs, getFAQCategories } from '@/lib/api';
import { FAQManager } from '@/components/dashboard/FAQManager';

export default async function FAQPage() {
  const [faqRes, catRes] = await Promise.all([
    getFAQs(),
    getFAQCategories(),
  ]);

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>❓ مدیریت سوالات متداول</h1>
      <FAQManager
        initialFAQs={faqRes.data?.results || faqRes.data || []}
        categories={catRes.data?.results || catRes.data || []}
      />
    </div>
  );
}