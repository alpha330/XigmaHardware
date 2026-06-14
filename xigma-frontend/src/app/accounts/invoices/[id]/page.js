// src/app/accounts/invoices/[id]/page.js
import InvoiceDetailClient from '../../../../../components/accounts/InvoiceDetailClient';

export const metadata = {
  title: 'جزئیات فاکتور | XigmaHardware',
};

export default async function InvoiceDetailPage({ params }) {
  // در Next.js 15 پارامترها باید await شوند
  const resolvedParams = await params;
  const id = resolvedParams.id;

  return <InvoiceDetailClient invoiceId={id} />;
}