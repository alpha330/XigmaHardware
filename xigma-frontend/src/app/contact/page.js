// src/app/contact/page.js
import ContactClient from '../../components/website/ContactClient';

export const metadata = {
  title: 'ارتباط با ما | XigmaHardware',
  description: 'برای مشاوره خرید سرور، پشتیبانی قطعات و ارتباط با تیم فروش XigmaHardware از طریق این صفحه با ما در تماس باشید.',
};

export default function ContactPage() {
  return <ContactClient />;
}