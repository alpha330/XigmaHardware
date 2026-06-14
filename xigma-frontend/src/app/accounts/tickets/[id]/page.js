// src/app/accounts/tickets/[id]/page.js
import TicketDetailClient from '../../../../components/support/TicketDetailClient';

export const metadata = {
  title: 'جزئیات تیکت | XigmaHardware',
};

export default async function TicketDetailPage({ params }) {
  const resolvedParams = await params;
  return <TicketDetailClient ticketId={resolvedParams.id} />;
}