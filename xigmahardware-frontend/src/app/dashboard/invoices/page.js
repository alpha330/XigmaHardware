import { getInvoices } from '@/lib/api';
import { InvoicesTable } from '@/components/dashboard/InvoicesTable';

export default async function InvoicesPage() {
  const { data } = await getInvoices();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>📋 فاکتورها</h1>
      <InvoicesTable invoices={data?.results || []} />
    </div>
  );
}