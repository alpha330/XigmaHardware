import ContentPageClient from '../../../components/website/ContentPageClient';
import { serverApiUrl } from '../../../utils/serverApiUrl';


async function getArticle(id) {
  try {
    const response = await fetch(
      serverApiUrl(`/api/v1/website/articles/${id}/`),
      { next: { revalidate: 3600 } },
    );
    if (!response.ok) throw new Error('Article not found');
    return response.json();
  } catch {
    return {
      title: 'مقاله در دسترس نیست',
      summary: 'در دریافت محتوای این مقاله مشکلی رخ داده است.',
      content: '<p>لطفاً کمی بعد دوباره تلاش کنید.</p>',
    };
  }
}

export default async function ArticlePage({ params }) {
  const { id } = await params;
  const article = await getArticle(id);

  return (
    <ContentPageClient
      title={article.title}
      summary={article.summary}
      content={article.content || article.body || '<p>محتوایی ثبت نشده است.</p>'}
    />
  );
}
