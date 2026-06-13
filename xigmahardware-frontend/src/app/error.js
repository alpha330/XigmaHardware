'use client';
/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react';
import { useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTriangleExclamation, faRotateRight } from '@fortawesome/free-solid-svg-icons';

const containerStyle = css`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
  text-align: center;
  color: #dc3545;

  .icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    color: #e94560;
    filter: drop-shadow(0 4px 8px rgba(233, 69, 96, 0.3));
  }

  h2 {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    color: #1a1a2e;
  }

  p {
    color: #666;
    margin-bottom: 2rem;
    max-width: 400px;
    line-height: 1.8;
  }

  button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.8rem 2rem;
    background: #0f3460;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s, transform 0.2s;

    &:hover {
      background: #e94560;
      transform: translateY(-2px);
    }
  }
`;

export default function Error({ error, reset }) {
  useEffect(() => {
    // می‌تونیم خطا رو به سیستم مانیتورینگ بفرستیم
    console.error('Global error:', error);
  }, [error]);

  return (
    <div css={containerStyle}>
      <div className="icon">
        <FontAwesomeIcon icon={faTriangleExclamation} />
      </div>
      <h2>متأسفانه مشکلی پیش آمده است</h2>
      <p>
        {error?.message || 'لطفاً دوباره تلاش کنید. در صورت ادامه مشکل با پشتیبانی تماس بگیرید.'}
      </p>
      <button onClick={() => reset()}>
        <FontAwesomeIcon icon={faRotateRight} />
        تلاش مجدد
      </button>
    </div>
  );
}