// src/app/market/product/[id]/page.js
import ProductDetailClient from '../../../../components/market/ProductDetailClient';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  // در یک پروژه واقعی، می‌توانید نام محصول را برای سئو از سرور دریافت کنید
  return {
    title: `جزئیات محصول | XigmaHardware`,
  };
}

export default async function ProductPage({ params }) {
  const resolvedParams = await params;
  const identifier = resolvedParams.id; // می‌تواند slug یا id باشد بسته به بک‌اند

  return <ProductDetailClient identifier={identifier} />;
}