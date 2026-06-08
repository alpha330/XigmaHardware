// src/components/product/ProductCard.js
'use client';

import styled from '@emotion/styled';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { faStar, faStarHalfStroke, faCartShopping, faHeart, faTruck } from '@fortawesome/free-solid-svg-icons';

const Card = styled.div`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  overflow: hidden;
  transition: all 0.25s;
  position: relative;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${p => p.theme.shadows.lg};
    border-color: ${p => p.theme.colors.brand[300]};
  }
`;

const ImageSection = styled.div`
  height: 220px;
  background: ${p => p.theme.colors.bg.tertiary};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  position: relative;

  @media (max-width: 480px) { height: 180px; font-size: 3rem; }
`;

const Badges = styled.div`
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
`;

const DiscountBadge = styled.span`
  padding: 4px 10px;
  background: ${p => p.theme.colors.danger};
  color: white;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
`;

const ShippingBadge = styled.span`
  padding: 4px 10px;
  background: ${p => p.theme.colors.success};
  color: white;
  border-radius: 50px;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const WishlistBtn = styled.button`
  position: absolute;
  top: 12px;
  right: 12px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(4px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${p => p.theme.colors.text.muted};
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);

  &:hover { color: ${p => p.theme.colors.danger}; transform: scale(1.1); }
`;

const Info = styled.div`
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const Title = styled(Link)`
  font-size: 0.9rem;
  font-weight: 600;
  color: ${p => p.theme.colors.text.primary};
  text-decoration: none;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 8px;
  line-height: 1.5;

  &:hover { color: ${p => p.theme.colors.brand[600]}; }
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
`;

const RatingText = styled.span`
  font-size: 0.8rem;
  color: ${p => p.theme.colors.text.muted};
  margin-right: 4px;
`;

const PriceRow = styled.div`
  margin-top: auto;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
`;

const Price = styled.div`
  .current {
    font-size: 1.15rem;
    font-weight: 700;
    color: ${p => p.theme.colors.text.primary};
  }
  .old {
    font-size: 0.8rem;
    color: ${p => p.theme.colors.text.muted};
    text-decoration: line-through;
    margin-right: 6px;
  }
  .currency {
    font-size: 0.7rem;
    font-weight: 400;
    color: ${p => p.theme.colors.text.muted};
    margin-right: 2px;
  }
`;

export const ProductCard = ({ product }) => {
  return (
    <Card>
      <ImageSection>
        {product.emoji || '🖥️'}
        <Badges>
          {product.discount > 0 && <DiscountBadge>-{product.discount}%</DiscountBadge>}
          {product.freeShipping && (
            <ShippingBadge><Icon icon={faTruck} size="xs" /> ارسال رایگان</ShippingBadge>
          )}
        </Badges>
        <WishlistBtn><Icon icon={faHeart} size="sm" /></WishlistBtn>
      </ImageSection>

      <Info>
        <Title href={`/products/${product.slug}`}>{product.title}</Title>

        <Rating>
          {[1,2,3,4,5].map(i => (
            <Icon
              key={i}
              icon={i <= Math.floor(product.rating) ? faStar : i <= product.rating ? faStarHalfStroke : faStar}
              size="xs"
              color={i <= product.rating ? '#f59e0b' : '#cbd5e1'}
            />
          ))}
          <RatingText>({product.reviews})</RatingText>
        </Rating>

        <PriceRow>
          <Price>
            <span className="currency">تومان</span>
            <span className="current">{product.price}</span>
            {product.oldPrice && <span className="old">{product.oldPrice}</span>}
          </Price>
          <Button variant="primary" size="sm" icon={faCartShopping}>
            افزودن
          </Button>
        </PriceRow>
      </Info>
    </Card>
  );
};