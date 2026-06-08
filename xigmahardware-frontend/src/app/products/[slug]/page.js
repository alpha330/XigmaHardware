import { getProduct } from '@/lib/api';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { ProductGallery } from '@/components/product/ProductGallery';
import { RatingStars } from '@/components/product/RatingStars';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import { faCartShopping, faHeart, faTruck, faShieldAlt, faRotateLeft } from '@fortawesome/free-solid-svg-icons';

export default async function ProductDetail({ params }) {
  const { slug } = await params;
  const { success, data } = await getProduct(slug);

  if (!success || !data) {
    return <div>محصول یافت نشد</div>;
  }

  const product = data.results?.[0] || data;

  return (
    <>
      <Header />
      <main style={{ maxWidth: 1440, margin: '96px auto 0', padding: '0 24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48 }}>
          <ProductGallery media={product.media || []} />
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, lineHeight: 1.3 }}>{product.title}</h1>
            <RatingStars rating={product.avg_rating} count={product.rating_count} />
            <div style={{ margin: '20px 0', fontSize: '1.5rem', fontWeight: 700 }}>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>تومان </span>
              {product.final_price?.toLocaleString() || product.market_price?.toLocaleString()}
              {product.has_discount && (
                <span style={{ textDecoration: 'line-through', color: '#94a3b8', marginRight: 12, fontSize: '1rem' }}>
                  {product.market_price?.toLocaleString()}
                </span>
              )}
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <Button variant="primary" size="lg" icon={faCartShopping}>افزودن به سبد</Button>
              <Button variant="outline" size="lg" icon={faHeart}>علاقه‌مندی</Button>
            </div>
            <div style={{ display: 'flex', gap: 32, marginTop: 32, padding: '20px 0', borderTop: '1px solid #e2e8f0' }}>
              <div><Icon icon={faTruck} /> ارسال سریع</div>
              <div><Icon icon={faShieldAlt} /> گارانتی معتبر</div>
              <div><Icon icon={faRotateLeft} /> بازگشت ۷ روزه</div>
            </div>
            <div style={{ marginTop: 32 }}>
              <h3>مشخصات فنی</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                {product.stock_info && Object.entries(product.stock_info).map(([k, v]) => (
                  v && <tr key={k} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '8px 12px', color: '#64748b' }}>{k}</td>
                    <td style={{ padding: '8px 12px' }}>{v}</td>
                  </tr>
                ))}
              </table>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}