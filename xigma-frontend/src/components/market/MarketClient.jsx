'use client';

import React, { useTransition } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import styled from '@emotion/styled';
import ProductCard from '../shared/ProductCard';

// ==================== STYLED COMPONENTS (Emotion) ====================
const PageWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px;
  display: flex;
  gap: 32px;
  @media (max-width: 900px) {
    flex-direction: column;
    gap: 24px;
  }
`;

const Sidebar = styled.aside`
  width: 280px;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
  align-self: flex-start;
  background: ${({ theme }) => theme.colors?.surface || '#fff'};
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
  @media (max-width: 900px) {
    position: static;
    width: 100%;
  }
`;

const MainContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const FilterTitle = styled.h3`
  font-size: 15px;
  font-weight: 700;
  color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
`;

const SearchInputWrapper = styled.div`
  position: relative;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 12px;
  font-size: 14px;
  background: ${({ theme }) => theme.colors?.background || '#f9fafb'};
  transition: all 0.2s ease;
  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 18px;
`;

const CategoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 24px;
`;

const CategoryItem = styled.a`
  display: flex;
  align-items: center;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  &[data-active='true'] {
    background: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    color: white;
    font-weight: 600;
  }
  &:hover {
    background: ${({ theme }) => theme.colors?.hover || '#f3f4f6'};
    color: ${({ theme }) => theme.colors?.textPrimary || '#111827'};
  }
`;

const BrandList = styled.div`
  max-height: 220px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-right: 4px;
  margin-bottom: 24px;
`;

const BrandItem = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  &:hover {
    background: #f8fafc;
  }
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  accent-color: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
`;

const PriceSection = styled.div`
  margin-bottom: 24px;
`;

const PriceGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
`;

const PriceField = styled.div``;

const PriceLabel = styled.div`
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
`;

const PriceInput = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 10px;
  font-size: 14px;
  text-align: center;
  box-sizing: border-box;
`;

const RangeSliderContainer = styled.div`
  position: relative;
  height: 6px;
  background: #e5e7eb;
  border-radius: 999px;
  margin: 20px 8px 12px;
`;

const RangeTrack = styled.div`
  position: absolute;
  height: 6px;
  background: ${({ theme }) => theme.colors?.primary || '#3b82f6'};
  border-radius: 999px;
  transition: all 0.1s ease;
`;

const RangeInput = styled.input`
  position: absolute;
  width: 100%;
  pointer-events: none;
  appearance: none;
  height: 6px;
  background: transparent;
  z-index: 2;
  &::-webkit-slider-thumb {
    pointer-events: all;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: white;
    border: 3px solid ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    cursor: pointer;
    margin-top: -6px;
    z-index: 3;
  }
  &::-moz-range-thumb {
    pointer-events: all;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: white;
    border: 3px solid ${({ theme }) => theme.colors?.primary || '#3b82f6'};
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    cursor: pointer;
  }
`;

const SortSelect = styled.select`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme.colors?.border || '#e5e7eb'};
  border-radius: 12px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  margin-bottom: 20px;
`;

const FilterRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
`;

const SwitchLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  cursor: pointer;
`;

const ActiveFilters = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
`;

const FilterChip = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  color: #334155;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
`;

const ClearButton = styled.button`
  background: none;
  border: none;
  color: #ef4444;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  &:hover { text-decoration: underline; }
`;

const TopBar = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
`;

const ResultCount = styled.div`
  font-size: 15px;
  color: ${({ theme }) => theme.colors?.textSecondary || '#4b5563'};
  font-weight: 500;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
  font-size: 15px;
`;

// ==================== MAIN COMPONENT ====================
export default function MarketClient({ products = [], categories = [], brands = [] }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  // Read current filters from URL
  const currentSearch = searchParams.get('search') || '';
  const currentCategory = searchParams.get('category') || '';
  const currentBrands = searchParams.get('brand') ? searchParams.get('brand').split(',').filter(Boolean) : [];
  const currentMinPrice = searchParams.get('min_price') || '';
  const currentMaxPrice = searchParams.get('max_price') || '';
  const currentSort = searchParams.get('sort') || 'newest';
  const currentInStock = searchParams.get('in_stock') === 'true';

  const MAX_PRICE = 500000000; // 500 میلیون تومان

  const updateFilters = (newParams) => {
    const params = new URLSearchParams(searchParams.toString());

    Object.entries(newParams).forEach(([key, value]) => {
      if (value === null || value === '' || (Array.isArray(value) && value.length === 0)) {
        params.delete(key);
      } else if (Array.isArray(value)) {
        params.set(key, value.join(','));
      } else {
        params.set(key, value);
      }
    });

    startTransition(() => {
      router.replace(`/market?${params.toString()}`, { scroll: false });
    });
  };

  // Handlers
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      updateFilters({ search: e.target.value.trim() || null, page: null });
    }
  };

  const handleCategoryClick = (catId) => {
    updateFilters({ category: catId || null, page: null });
  };

  const toggleBrand = (brandId) => {
    const newBrands = currentBrands.includes(String(brandId))
      ? currentBrands.filter(id => id !== String(brandId))
      : [...currentBrands, String(brandId)];
    updateFilters({ brand: newBrands.length > 0 ? newBrands : null, page: null });
  };

  const handlePriceChange = (type, value) => {
    let num = value === '' ? null : parseInt(value, 10);
    if (num !== null) {
      if (type === 'min') num = Math.max(0, Math.min(num, parseInt(currentMaxPrice) || MAX_PRICE));
      else num = Math.min(MAX_PRICE, Math.max(num, parseInt(currentMinPrice) || 0));
    }
    if (type === 'min') updateFilters({ min_price: num, page: null });
    else updateFilters({ max_price: num, page: null });
  };

  const handleSortChange = (e) => {
    updateFilters({ sort: e.target.value, page: null });
  };

  const handleInStockChange = (e) => {
    updateFilters({ in_stock: e.target.checked ? 'true' : null, page: null });
  };

  const clearAllFilters = () => {
    router.replace('/market', { scroll: false });
  };

  // Calculate slider percentages
  const minVal = parseInt(currentMinPrice) || 0;
  const maxVal = parseInt(currentMaxPrice) || MAX_PRICE;
  const minPercent = Math.min(Math.max((minVal / MAX_PRICE) * 100, 0), 100);
  const maxPercent = Math.min(Math.max((maxVal / MAX_PRICE) * 100, 0), 100);

  // Active filters for chips
  const activeFilters = [];
  if (currentSearch) activeFilters.push({ label: `جستجو: ${currentSearch}`, key: 'search' });
  if (currentCategory) {
    const cat = categories.find(c => String(c.id) === currentCategory);
    if (cat) activeFilters.push({ label: cat.name || cat.title, key: 'category' });
  }
  currentBrands.forEach(brandId => {
    const brand = brands.find(b => String(b.id) === brandId);
    if (brand) activeFilters.push({ label: brand.persian_name || brand.name, key: `brand-${brandId}`, brandId });
  });
  if (currentMinPrice || currentMaxPrice) {
    activeFilters.push({ label: `قیمت: ${currentMinPrice || '0'} - ${currentMaxPrice || '∞'}`, key: 'price' });
  }
  if (currentInStock) activeFilters.push({ label: 'فقط موجود', key: 'in_stock' });

  const removeFilter = (filter) => {
    if (filter.key === 'search') updateFilters({ search: null });
    else if (filter.key === 'category') updateFilters({ category: null });
    else if (filter.key === 'price') updateFilters({ min_price: null, max_price: null });
    else if (filter.key === 'in_stock') updateFilters({ in_stock: null });
    else if (filter.key.startsWith('brand-')) {
      const newBrands = currentBrands.filter(id => id !== filter.brandId);
      updateFilters({ brand: newBrands.length ? newBrands : null });
    }
  };

  return (
    <PageWrapper>
      {/* SIDEBAR FILTERS */}
      <Sidebar>
        <FilterTitle>جستجو و فیلترها</FilterTitle>

        {/* Search */}
        <SearchInputWrapper>
          <SearchIcon>🔍</SearchIcon>
          <SearchInput
            type="text"
            placeholder="جستجو در محصولات..."
            defaultValue={currentSearch}
            onKeyDown={handleSearch}
          />
        </SearchInputWrapper>

        {/* Categories */}
        <FilterTitle>دسته‌بندی‌ها</FilterTitle>
        <CategoryList>
          <CategoryItem
            href="/market"
            data-active={!currentCategory ? 'true' : 'false'}
            onClick={(e) => { e.preventDefault(); handleCategoryClick(''); }}
          >
            همه محصولات
          </CategoryItem>
          {categories.map((cat) => (
            <CategoryItem
              key={cat.id}
              href={`/market?category=${cat.id}`}
              data-active={currentCategory === String(cat.id) ? 'true' : 'false'}
              onClick={(e) => { e.preventDefault(); handleCategoryClick(cat.id); }}
            >
              {cat.name || cat.title}
            </CategoryItem>
          ))}
        </CategoryList>

        {/* Brands - Multi select */}
        {brands.length > 0 && (
          <>
            <FilterTitle>برندها</FilterTitle>
            <BrandList>
              {brands.map((brand) => {
                const isSelected = currentBrands.includes(String(brand.id));
                return (
                  <BrandItem key={brand.id}>
                    <Checkbox
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleBrand(brand.id)}
                    />
                    {brand.persian_name || brand.name}
                  </BrandItem>
                );
              })}
            </BrandList>
          </>
        )}

        {/* Price Range with improved dual slider */}
        <PriceSection>
          <FilterTitle>بازه قیمت (تومان)</FilterTitle>

          <PriceGrid>
            <PriceField>
              <PriceLabel>حداقل</PriceLabel>
              <PriceInput
                type="number"
                placeholder="0"
                value={currentMinPrice}
                onChange={(e) => handlePriceChange('min', e.target.value)}
              />
            </PriceField>
            <PriceField>
              <PriceLabel>حداکثر</PriceLabel>
              <PriceInput
                type="number"
                placeholder="500,000,000"
                value={currentMaxPrice}
                onChange={(e) => handlePriceChange('max', e.target.value)}
              />
            </PriceField>
          </PriceGrid>

          {/* Dual Range Slider */}
          <RangeSliderContainer>
            <RangeTrack
              style={{
                left: `${minPercent}%`,
                width: `${Math.max(maxPercent - minPercent, 0)}%`
              }}
            />
            {/* Min thumb */}
            <RangeInput
              type="range"
              min="0"
              max={MAX_PRICE}
              step="1000000"
              value={minVal}
              onChange={(e) => {
                const newMin = Math.min(parseInt(e.target.value), maxVal - 1000000);
                handlePriceChange('min', newMin);
              }}
            />
            {/* Max thumb */}
            <RangeInput
              type="range"
              min="0"
              max={MAX_PRICE}
              step="1000000"
              value={maxVal}
              onChange={(e) => {
                const newMax = Math.max(parseInt(e.target.value), minVal + 1000000);
                handlePriceChange('max', newMax);
              }}
            />
          </RangeSliderContainer>

          <div style={{ fontSize: '11px', color: '#9ca3af', textAlign: 'center', marginTop: '4px' }}>
            از {minVal.toLocaleString('fa-IR')} تا {maxVal.toLocaleString('fa-IR')} تومان
          </div>
        </PriceSection>

        {/* Sort */}
        <FilterTitle>مرتب‌سازی</FilterTitle>
        <SortSelect value={currentSort} onChange={handleSortChange}>
          <option value="newest">جدیدترین</option>
          <option value="price_asc">ارزان‌ترین</option>
          <option value="price_desc">گران‌ترین</option>
          <option value="rating">بالاترین امتیاز</option>
          <option value="popular">محبوب‌ترین</option>
        </SortSelect>

        {/* In Stock */}
        <FilterRow>
          <SwitchLabel>
            <input
              type="checkbox"
              checked={currentInStock}
              onChange={handleInStockChange}
            />
            فقط موجود در انبار
          </SwitchLabel>
        </FilterRow>

        {/* Active Filters */}
        {activeFilters.length > 0 && (
          <>
            <FilterTitle style={{ marginTop: '24px' }}>فیلترهای فعال</FilterTitle>
            <ActiveFilters>
              {activeFilters.map((filter, index) => (
                <FilterChip key={index}>
                  {filter.label}
                  <span
                    onClick={() => removeFilter(filter)}
                    style={{ cursor: 'pointer', marginLeft: '4px', fontWeight: 'bold' }}
                  >×</span>
                </FilterChip>
              ))}
            </ActiveFilters>
            <ClearButton onClick={clearAllFilters}>پاک کردن همه فیلترها
            </ClearButton>
          </>
        )}
      </Sidebar>

      {/* MAIN CONTENT */}
      <MainContent>
        <TopBar>
          <ResultCount>
            {products.length} محصول یافت شد
          </ResultCount>
        </TopBar>

        {products.length > 0 ? (
          <Grid>
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </Grid>
        ) : (
          <EmptyState>
            محصولی با این فیلترها یافت نشد.<br />
            فیلترها را تغییر دهید یا پاک کنید.
          </EmptyState>
        )}
      </MainContent>
    </PageWrapper>
  );
}
