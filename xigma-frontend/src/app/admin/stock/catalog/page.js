// src/app/admin/stock/catalog/page.js
import AdminCatalogClient from '../../../../components/admin/stock/AdminCatalogClient';

export const metadata = {
  title: 'مدیریت کاتالوگ | پنل ادمین',
};

export default function AdminCatalogPage() {
  return <AdminCatalogClient />;
}