import { getMyShipments } from '@/lib/api';
import { ShipmentsTable } from '@/components/dashboard/ShipmentsTable';

export default async function ShipmentsPage() {
  const { data } = await getMyShipments();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>🚚 محموله‌ها</h1>
      <ShipmentsTable shipments={data?.results || []} />
    </div>
  );
}