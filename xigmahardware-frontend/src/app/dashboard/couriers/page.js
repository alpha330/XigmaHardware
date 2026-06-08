// src/app/dashboard/couriers/page.js
import { getCouriers } from '@/lib/api';
import { CouriersList } from '@/components/dashboard/CouriersList';
import { Button } from '@/components/ui/Button';

export default async function CouriersPage() {
  const { data } = await getCouriers();
  const couriers = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>🛵 پیک‌ها</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/couriers/new'}>
          افزودن پیک جدید
        </Button>
      </div>
      <CouriersList couriers={couriers} />
    </div>
  );
}