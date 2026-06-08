// src/app/dashboard/inventory/page.js
import { getInventoryItems } from '@/lib/api';
import { InventoryTable } from '@/components/dashboard/InventoryTable';
import { Button } from '@/components/ui/Button';

export default async function InventoryPage({ searchParams }) {
  const params = await searchParams;
  const warehouseId = params.warehouse || '';
  const lowStock = params.low_stock || '';
  const search = params.search || '';

  const query = {};
  if (warehouseId) query.warehouse = warehouseId;
  if (lowStock) query.low_stock = 'true';
  if (search) query.search = search;

  const { data } = await getInventoryItems(query);
  const items = data?.results || data || [];

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>📦 موجودی انبار</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/inventory/add'}>
          افزودن موجودی
        </Button>
      </div>
      <InventoryTable items={items} warehouseFilter={warehouseId} searchQuery={search} />
    </div>
  );
}