// src/app/basket/wishlists/[id]/page.js
import WishlistDetailClient from '../../../../components/basket/WishlistDetailClient';

export const metadata = {
  title: 'جزئیات پیش‌فاکتور | XigmaHardware',
};

export default async function WishlistDetailPage({ params }) {
  // بر اساس ساختار استاندارد نکست ۱۵ پارامترها به صورت آسنکرون دریافت می‌شوند
  const resolvedParams = await params;
  const id = resolvedParams.id;

  return <WishlistDetailClient wishlistId={id} />;
}