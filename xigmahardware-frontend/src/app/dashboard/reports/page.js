import { getReports } from '@/lib/api';
import { ReportsView } from '@/components/dashboard/ReportsView';

export default async function ReportsPage() {
  const { data } = await getReports();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>📊 گزارش‌ها</h1>
      <ReportsView reports={data?.results || []} />
    </div>
  );
}