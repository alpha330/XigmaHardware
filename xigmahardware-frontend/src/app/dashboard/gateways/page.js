// src/app/dashboard/gateways/page.js
import { getGateways } from '@/lib/api';
import { GatewaysList } from '@/components/dashboard/GatewaysList';
import { Button } from '@/components/ui/Button';

export default async function GatewaysPage() {
  const { data } = await getGateways();
  const gateways = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>💳 درگاه‌های پرداخت</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/gateways/new'}>
          افزودن درگاه
        </Button>
      </div>
      <GatewaysList gateways={gateways} />
    </div>
  );
}