// src/app/admin/stock/products/page.js
import AdminProductsClient from '../../../../components/admin/stock/AdminProductsClient';

export const metadata = {
  title: 'مدیریت کالاها و انبار | پنل ادمین',
};

export default function AdminProductsPage() {
  return <AdminProductsClient />;
}