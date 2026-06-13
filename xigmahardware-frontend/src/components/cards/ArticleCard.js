'use client';
/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';
import Link from 'next/link';
import { toJalali } from '@/utils/format';

const cardStyles = css`
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.3s;
  &:hover { transform: translateY(-3px); }
  img { width: 100%; height: 180px; object-fit: cover; }
  .content { padding: 1rem; }
  h3 { font-size: 1.1rem; margin-bottom: 0.5rem; }
  p { color: #666; font-size: 0.9rem; }
  .date { font-size: 0.8rem; color: #999; margin-top: 0.5rem; }
`;

export default function ArticleCard({ article }) {
  return (
    <div css={cardStyles}>
      <Link href={`/articles/${article.slug}`}>
        <img src={article.image_url || '/images/placeholder.png'} alt={article.title} />
      </Link>
      <div className="content">
        <Link href={`/articles/${article.slug}`}><h3>{article.title}</h3></Link>
        <p>{article.excerpt?.slice(0, 100)}...</p>
        <div className="date">{toJalali(article.published_at, 'date')}</div>
      </div>
    </div>
  );
}