// src/app/dashboard/reviews/page.js
import { getMyReviews } from '@/lib/api';
import { ReviewsList } from '@/components/dashboard/ReviewsList';

export default async function ReviewsPage() {
  const { data } = await getMyReviews();
  const reviews = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>⭐ نظرات من</h1>
      <ReviewsList reviews={reviews} />
    </div>
  );
}