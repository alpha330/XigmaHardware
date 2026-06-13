import { ThemeProvider } from '@/lib/ThemeContext';
import { GlobalStyles } from '@/styles/global';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import ToastProvider from '@/components/layout/ToastProvider';

export const metadata = {
  title: 'XigmaHardware - فروشگاه سخت‌افزار',
  description: 'مرجع تخصصی خرید قطعات سرور، تجهیزات شبکه و قطعات کامپیوتر',
  keywords: 'سرور, قطعات کامپیوتر, Xigma, خرید سرور',
  openGraph: {
    title: 'XigmaHardware',
    description: 'فروشگاه آنلاین سخت‌افزار',
    url: 'https://xigmahardware.com',
    siteName: 'XigmaHardware',
    locale: 'fa_IR',
    type: 'website',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="fa" dir="rtl">
      <body>
        <ThemeProvider>
          <GlobalStyles />
          <ToastProvider>
            <Header />
            <main style={{ minHeight: '80vh' }}>{children}</main>
            <Footer />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}