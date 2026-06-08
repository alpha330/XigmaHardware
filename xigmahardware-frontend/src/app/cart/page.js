// src/app/cart/page.js
import { getCart } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { CartClient } from '@/components/cart/CartClient';

export const metadata = {
  title: 'سبد خرید | XigmaHardware',
};

export default async function CartPage() {
  const res = await getCart();
  const cart = res.success ? res.data : null;

  return (
    <>
      <Header />
      <main style={{ maxWidth: 1200, margin: '96px auto 0', padding: '0 24px', minHeight: '60vh' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 32 }}>🛒 سبد خرید</h1>
        <CartClient initialCart={cart} />
      </main>
      <Footer />
    </>
  );
}