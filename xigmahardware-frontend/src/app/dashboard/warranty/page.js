import { getWarranties } from '@/lib/api';
import { WarrantyList } from '@/components/dashboard/WarrantyList';

export default async function WarrantyPage() {
  const { data } = await getWarranties();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>🛡️ گارانتی‌ها</h1>
      <WarrantyList warranties={data?.results || []} />
    </div>
  );
}