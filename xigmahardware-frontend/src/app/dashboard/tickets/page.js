import { getTickets } from '@/lib/api';
import { TicketList } from '@/components/dashboard/TicketList';
import { Button } from '@/components/ui/Button';

export default async function TicketsPage() {
  const { data } = await getTickets();
  const tickets = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>🎫 تیکت‌های پشتیبانی</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/tickets/new'}>
          تیکت جدید
        </Button>
      </div>
      <TicketList tickets={tickets} />
    </div>
  );
}