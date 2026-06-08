import { getMyInvoices } from '@/lib/api';
import { OrdersList } from '@/components/dashboard/OrdersList';

export default async function OrdersPage() {
  const { data, error } = await getMyInvoices();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>
        📦 سفارشات من
      </h1>
      <OrdersList invoices={data?.results || []} error={error} />
    </div>
  );
}