import ContentPageClient from '../../components/website/ContentPageClient';
import { serverApiUrl } from '../../utils/serverApiUrl';


export const metadata = {
  title: 'قوانین و مقررات | XigmaHardware',
};

async function getTerms() {
  try {
    const response = await fetch(
      serverApiUrl('/api/v1/website/pages/terms/'),
      { next: { revalidate: 3600 } },
    );
    if (!response.ok) throw new Error('Terms page not found');
    return response.json();
  } catch {
    return {
      title: 'قوانین و مقررات',
      summary: 'نسخه نهایی قوانین پس از تأیید واحد حقوقی در همین صفحه منتشر می‌شود.',
      content: '<p>برای اطلاع از شرایط خرید، ارسال، مرجوعی و گارانتی با واحد پشتیبانی XigmaHardware تماس بگیرید.</p>',
    };
  }
}

export default async function TermsPage() {
  const page = await getTerms();

  return (
    <ContentPageClient
      title={page.title || 'قوانین و مقررات'}
      summary={page.summary}
      content={page.content || page.body || '<p>محتوایی ثبت نشده است.</p>'}
    />
  );
}
