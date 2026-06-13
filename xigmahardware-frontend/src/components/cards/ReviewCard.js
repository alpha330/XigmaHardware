'use client';
/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';
import { toJalali } from '@/utils/format';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar, faQuoteRight } from '@fortawesome/free-solid-svg-icons';

const cardStyles = css`
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  .quote { color: #e94560; font-size: 2rem; margin-bottom: 0.5rem; }
  .rating { color: #ffc107; margin-bottom: 0.8rem; }
  p { color: #555; font-style: italic; }
  .author { margin-top: 1rem; font-weight: bold; }
  .date { font-size: 0.8rem; color: #999; }
`;

export default function ReviewCard({ review }) {
  return (
    <div css={cardStyles}>
      <div className="quote"><FontAwesomeIcon icon={faQuoteRight} /></div>
      <div className="rating">
        {Array.from({ length: review.rating_overall || 5 }).map((_, i) => (
          <FontAwesomeIcon key={i} icon={faStar} />
        ))}
      </div>
      <p>{review.body?.slice(0, 150)}...</p>
      <div className="author">{review.user_name}</div>
      <div className="date">{toJalali(review.created_at, 'date')}</div>
    </div>
  );
}