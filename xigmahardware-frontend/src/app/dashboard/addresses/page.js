import { getAddresses } from '@/lib/api';
import { AddressList } from '@/components/dashboard/AddressList';
import { Button } from '@/components/ui/Button';

export default async function AddressesPage() {
  const { data } = await getAddresses();
  const addresses = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>📍 آدرس‌های من</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/addresses/new'}>
          افزودن آدرس جدید
        </Button>
      </div>
      <AddressList addresses={addresses} />
    </div>
  );
}