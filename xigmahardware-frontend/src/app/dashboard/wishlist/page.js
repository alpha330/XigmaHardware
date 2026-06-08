// src/app/dashboard/wishlist/page.js
import { getWishlists } from '@/lib/api';
import { WishlistGrid } from '@/components/dashboard/WishlistGrid';

export default async function WishlistPage() {
  const { data } = await getWishlists();
  const wishlists = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>❤️ علاقه‌مندی‌ها</h1>
      <WishlistGrid wishlists={wishlists} />
    </div>
  );
}