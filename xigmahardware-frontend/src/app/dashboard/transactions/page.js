import { getTransactions } from '@/lib/api';
import { TransactionsTable } from '@/components/dashboard/TransactionsTable';

export default async function TransactionsPage() {
  const { data } = await getTransactions();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>💳 تراکنش‌ها</h1>
      <TransactionsTable transactions={data?.results || []} />
    </div>
  );
}