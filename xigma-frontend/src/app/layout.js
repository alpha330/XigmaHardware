// src/app/layout.js
import { Vazirmatn } from 'next/font/google';
import ThemeRegistry from '../theme/ThemeRegistry';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import LiveChatWidget from '../components/support/LiveChatWidget';
import { CartProvider } from '../context/CartContext';
import "@/styles/global.css"

const vazirmatn = Vazirmatn({
  subsets: ['latin', 'arabic'],
  display: 'swap',
  variable: '--font-vazirmatn',
});

export const metadata = {
  title: 'XigmaHardware | فروشگاه آنلاین تجهیزات شبکه و کامپیوتر',
  description: 'خرید انواع سرور، تجهیزات رادیویی، دیتاسنتر، PC و ورک‌استیشن با بهترین قیمت',
};

export default function RootLayout({ children }) {
  return (
    <html lang="fa" dir="rtl" className={vazirmatn.variable}>
      <body style={{ fontFamily: 'var(--font-vazirmatn)' }}>
        <ThemeRegistry>
          {/* ساختار بندی اصلی صفحه */}
          <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Header />
            <main style={{ flex: 1 }}>
              <CartProvider>
                {children}
              </CartProvider>
            </main>
            <Footer />
          </div>
          <LiveChatWidget />
        </ThemeRegistry>
      </body>
    </html>
  );
}
