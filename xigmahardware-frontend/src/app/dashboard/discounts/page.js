// src/app/dashboard/discounts/page.js
import { getWishlists } from '@/lib/api';
import { DiscountsList } from '@/components/dashboard/DiscountsList';

export default async function DiscountsPage() {
  const { data } = await getWishlists();
  const wishlists = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>🏷️ مدیریت تخفیف‌ها</h1>
      <DiscountsList wishlists={wishlists} />
    </div>
  );
}