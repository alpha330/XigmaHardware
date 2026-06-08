// src/app/checkout/page.js
import { getAddresses, getWallet, getCart } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { CheckoutClient } from '@/components/checkout/CheckoutClient';

export const metadata = {
  title: 'پرداخت | XigmaHardware',
};

export default async function CheckoutPage() {
  const [addressesRes, walletRes, cartRes] = await Promise.all([
    getAddresses(),
    getWallet(),
    getCart(),
  ]);

  return (
    <>
      <Header />
      <main style={{ maxWidth: 900, margin: '96px auto 0', padding: '0 24px', minHeight: '60vh' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 32 }}>💳 تکمیل خرید</h1>
        <CheckoutClient
          initialAddresses={addressesRes.success ? addressesRes.data : []}
          initialWallet={walletRes.success ? walletRes.data : null}
          initialCart={cartRes.success ? cartRes.data : null}
        />
      </main>
      <Footer />
    </>
  );
}