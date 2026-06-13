'use client';
/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';
import Link from 'next/link';
import { formatPrice, discountPercent, toJalali } from '@/utils/format';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar, faStarHalfAlt, faHeart, faShoppingCart } from '@fortawesome/free-solid-svg-icons';

const cardStyles = css`
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.3s, box-shadow 0.3s;
  &:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.12); }
  .product-image {
    height: 200px;
    background: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    img { max-height: 160px; object-fit: contain; }
    .discount-badge {
      position: absolute;
      top: 10px;
      left: 10px;
      background: #e94560;
      color: #fff;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.8rem;
    }
    .wishlist-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #fff;
      border: none;
      border-radius: 50%;
      width: 35px; height: 35px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
      color: #ccc;
      &:hover { color: #e94560; }
    }
  }
  .product-info {
    padding: 1rem;
    h3 { font-size: 1rem; margin-bottom: 0.5rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .rating { color: #ffc107; font-size: 0.9rem; margin-bottom: 0.5rem; }
    .price {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      .original { text-decoration: line-through; color: #999; font-size: 0.9rem; }
      .discounted { color: #e94560; font-weight: bold; font-size: 1.1rem; }
    }
    .add-to-cart {
      margin-top: 0.8rem;
      width: 100%;
      padding: 0.6rem;
      background: #0f3460;
      color: #fff;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.3s;
      &:hover { background: #e94560; }
    }
  }
`;

export default function ProductCard({ product }) {
  const disc = discountPercent(product.market_price, product.final_price);
  return (
    <div css={cardStyles}>
      <div className="product-image">
        <Link href={`/products/${product.slug}`}>
          <img src={product.main_image || '/images/placeholder.png'} alt={product.title} />
        </Link>
        {disc > 0 && <span className="discount-badge">-{disc}%</span>}
        <button className="wishlist-btn"><FontAwesomeIcon icon={faHeart} /></button>
      </div>
      <div className="product-info">
        <Link href={`/products/${product.slug}`}><h3>{product.title}</h3></Link>
        <div className="rating">
          <FontAwesomeIcon icon={faStar} /> {product.avg_rating?.toFixed(1) || '0'} ({product.rating_count || 0})
        </div>
        <div className="price">
          {disc > 0 && <span className="original">{formatPrice(product.market_price)}</span>}
          <span className="discounted">{formatPrice(product.final_price)}</span>
        </div>
        <button className="add-to-cart"><FontAwesomeIcon icon={faShoppingCart} /> افزودن به سبد</button>
      </div>
    </div>
  );
}