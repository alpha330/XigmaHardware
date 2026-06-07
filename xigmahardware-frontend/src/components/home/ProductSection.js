// src/components/home/ProductSection.js
'use client';

import styled from '@emotion/styled';
import { Button } from '@/components/ui/Button';
import { Icon } from '@/components/ui/Icon';
import {
  faStar, faStarHalfAlt, faShoppingCart, faHeart,
  faChevronLeft
} from '@fortawesome/free-solid-svg-icons';

const Section = styled.section`
  max-width: 1400px;
  margin: 60px auto;
  padding: 0 24px;
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const SectionTitle = styled.h2`
  font-size: 1.8rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text.primary};
  position: relative;
  padding-right: 16px;

  &::before {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 32px;
    background: ${props => props.theme.colors.primary[500]};
    border-radius: 2px;
  }
`;

const ProductGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
`;

const ProductCard = styled.div`
  background: ${props => props.theme.colors.card};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  overflow: hidden;
  transition: all 0.3s;
  animation: fadeIn 0.5s ease-out;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.primary[300]};
  }
`;

const ProductImage = styled.div`
  height: 220px;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.gray[100]},
    ${props => props.theme.colors.gray[50]}
  );
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  position: relative;
`;

const DiscountBadge = styled.span`
  position: absolute;
  top: 12px;
  left: 12px;
  background: ${props => props.theme.colors.danger};
  color: white;
  padding: 4px 10px;
  border-radius: ${props => props.theme.borderRadius.full};
  font-size: 0.8rem;
  font-weight: 600;
`;

const WishlistButton = styled.button`
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    color: ${props => props.theme.colors.danger};
  }
`;

const ProductInfo = styled.div`
  padding: 16px;
`;

const ProductTitle = styled.h3`
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: ${props => props.theme.colors.text.primary};
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
  font-size: 0.85rem;
  color: ${props => props.theme.colors.warning};
`;

const PriceRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Price = styled.div`
  font-size: 1.2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text.primary};

  .currency {
    font-size: 0.7rem;
    color: ${props => props.theme.colors.text.muted};
    margin-right: 4px;
  }
`;

const OldPrice = styled.span`
  font-size: 0.85rem;
  color: ${props => props.theme.colors.text.muted};
  text-decoration: line-through;
  margin-right: 8px;
`;

// Mock Data
const products = [
  { id: 1, title: 'سرور HP ProLiant DL380 G10', price: '۲۵۰,۰۰۰,۰۰۰', oldPrice: '۲۸۰,۰۰۰,۰۰۰', discount: 15, rating: 4.5, reviews: 128, emoji: '🖥️' },
  { id: 2, title: 'Dell PowerEdge R740', price: '۳۲۰,۰۰۰,۰۰۰', oldPrice: null, discount: null, rating: 4.8, reviews: 95, emoji: '🖥️' },
  { id: 3, title: 'Workstation HP Z8 G4', price: '۱۸۰,۰۰۰,۰۰۰', oldPrice: '۲۰۰,۰۰۰,۰۰۰', discount: 10, rating: 4.3, reviews: 64, emoji: '💻' },
  { id: 4, title: 'Cisco Switch C9300-24T', price: '۸۵,۰۰۰,۰۰۰', oldPrice: null, discount: null, rating: 4.7, reviews: 210, emoji: '🔌' },
  { id: 5, title: 'QNAP TS-453D NAS 4Bay', price: '۴۵,۰۰۰,۰۰۰', oldPrice: '۵۵,۰۰۰,۰۰۰', discount: 18, rating: 4.4, reviews: 82, emoji: '💾' },
  { id: 6, title: 'Lenovo ThinkSystem SR650', price: '۲۹۰,۰۰۰,۰۰۰', oldPrice: null, discount: null, rating: 4.6, reviews: 47, emoji: '🖥️' },
  { id: 7, title: 'RAM DDR4 32GB ECC Samsung', price: '۱۲,۰۰۰,۰۰۰', oldPrice: '۱۵,۰۰۰,۰۰۰', discount: 20, rating: 4.9, reviews: 350, emoji: '🔧' },
  { id: 8, title: 'SSD Samsung 870 EVO 1TB', price: '۴,۵۰۰,۰۰۰', oldPrice: null, discount: null, rating: 4.2, reviews: 180, emoji: '💿' },
];

export const ProductSection = ({ title, products: productList = products }) => {
  return (
    <Section>
      <SectionHeader>
        <SectionTitle>{title || 'محصولات'}</SectionTitle>
        <Button variant="ghost" size="sm" icon={faChevronLeft}>
          مشاهده همه
        </Button>
      </SectionHeader>

      <ProductGrid>
        {productList.map((product) => (
          <ProductCard key={product.id}>
            <ProductImage>
              {product.emoji}
              {product.discount && (
                <DiscountBadge>-{product.discount}%</DiscountBadge>
              )}
              <WishlistButton>
                <Icon icon={faHeart} size="sm" />
              </WishlistButton>
            </ProductImage>

            <ProductInfo>
              <ProductTitle>{product.title}</ProductTitle>
              <Rating>
                {[...Array(5)].map((_, i) => (
                  <Icon
                    key={i}
                    icon={i < Math.floor(product.rating) ? faStar : faStarHalfAlt}
                    size="xs"
                  />
                ))}
                <span style={{ color: '#888', marginRight: 4 }}>
                  ({product.reviews})
                </span>
              </Rating>
              <PriceRow>
                <Price>
                  <span className="currency">تومان</span>
                  {product.price}
                  {product.oldPrice && (
                    <OldPrice>{product.oldPrice}</OldPrice>
                  )}
                </Price>
                <Button variant="primary" size="sm" icon={faShoppingCart}>
                  افزودن
                </Button>
              </PriceRow>
            </ProductInfo>
          </ProductCard>
        ))}
      </ProductGrid>
    </Section>
  );
};