import { getFeaturedProducts, getBrands, getCategories, getNews, getReviews } from '@/lib/api';
import HeroSection from '@/components/home/HeroSection';
import BrandSlider from '@/components/home/BrandSlider';
import CategoryGrid from '@/components/home/CategoryGrid';
import FeaturedProducts from '@/components/home/FeaturedProducts';
import NewsSection from '@/components/home/NewsSection';
import ReviewSection from '@/components/home/ReviewSection';

export default async function HomePage() {
  // تمام fetch ها سمت سرور انجام می‌شود (SSR)
  const [featuredProducts, brands, categories, news, reviews] = await Promise.all([
    getFeaturedProducts().catch(() => []),
    getBrands().catch(() => []),
    getCategories().catch(() => []),
    getNews().catch(() => []),
    getReviews().catch(() => []),
  ]);

  return (
    <>
      <HeroSection />
      <BrandSlider brands={brands} />
      <CategoryGrid categories={categories} />
      <FeaturedProducts products={featuredProducts} />
      <NewsSection news={news} />
      <ReviewSection reviews={reviews} />
    </>
  );
}