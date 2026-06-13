// src/components/layout/SearchBar.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const SearchContainer = styled.div`
  position: relative;
  width: 100%;
  max-width: 400px;
  z-index: 100;
`;

const InputWrapper = styled.div`
  display: flex;
  align-items: center;
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme, isFocused }) => isFocused ? theme.colors.primary : theme.colors.border};
  border-radius: 8px;
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
  box-shadow: ${({ theme, isFocused }) => isFocused ? `0 0 0 3px ${theme.colors.primary}33` : 'none'};
`;

const SearchInput = styled.input`
  border: none;
  background: transparent;
  outline: none;
  width: 100%;
  color: ${({ theme }) => theme.colors.textMain};
  font-family: inherit;
  font-size: 0.95rem;

  &::placeholder {
    color: ${({ theme }) => theme.colors.textMuted};
  }
`;

const Dropdown = styled.div`
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ResultItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.background};
  }

  &:last-child {
    border-bottom: none;
  }
`;

const ResultInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
`;

const ResultName = styled.span`
  color: ${({ theme }) => theme.colors.textMain};
  font-size: 0.9rem;
  font-weight: bold;
`;

const ResultPrice = styled.span`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 0.85rem;
`;

const LoadingText = styled.div`
  padding: 1rem;
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.9rem;
`;

const ViewAllBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.primary};
  border: none;
  padding: 0.8rem;
  font-weight: bold;
  cursor: pointer;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  transition: background-color 0.2s ease;

  &:hover {
    background-color: ${({ theme }) => `${theme.colors.primary}10`};
  }
`;

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const containerRef = useRef(null);
  const router = useRouter();

  // بستن پاپ‌آپ وقتی کاربر بیرون از کادر جستجو کلیک می‌کند
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // افکت Debounce برای جستجو
  useEffect(() => {
    if (query.trim().length < 2) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setResults([]);
      setIsOpen(false);
      return;
    }

    const fetchResults = async () => {
      setIsLoading(true);
      setIsOpen(true);
      try {
        // اندپوینت سرچ (با استفاده از query string)
        const res = await fetch(`http://localhost:8000/api/v1/market/products/?search=${encodeURIComponent(query)}`);
        const data = await res.json();

        // استخراج آرایه (با توجه به صفحه‌بندی احتمالی)
        const items = Array.isArray(data) ? data : (data.results || []);
        setResults(items.slice(0, 4)); // فقط 4 نتیجه اول رو نشون میدیم
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchResults();
    }, 500); // 500 میلی‌ثانیه تاخیر بعد از آخرین کلید فشرده شده

    return () => clearTimeout(delayDebounceFn);
  }, [query]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setIsOpen(false);
      router.push(`/market?search=${encodeURIComponent(query)}`);
    }
  };

  return (
    <SearchContainer ref={containerRef}>
      <form onSubmit={handleSearchSubmit}>
        <InputWrapper isFocused={isFocused}>
          <SearchInput
            type="text"
            placeholder="جستجوی محصول، سرور، برند..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => {
              setIsFocused(true);
              if (query.trim().length >= 2) setIsOpen(true);
            }}
            onBlur={() => setIsFocused(false)}
          />
          <span style={{ color: 'var(--textMuted)', cursor: 'pointer' }} onClick={handleSearchSubmit}>
            🔍
          </span>
        </InputWrapper>
      </form>

      {isOpen && (
        <Dropdown>
          {isLoading ? (
            <LoadingText>در حال جستجو...</LoadingText>
          ) : results.length > 0 ? (
            <>
              {results.map((product) => (
                <ResultItem key={product.id} href={`/market/products/${product.id}`} onClick={() => setIsOpen(false)}>
                  <ResultInfo>
                    <ResultName>{product.name}</ResultName>
                    <ResultPrice>
                      {new Intl.NumberFormat('fa-IR').format(product.market_price || 0)} تومان
                    </ResultPrice>
                  </ResultInfo>
                </ResultItem>
              ))}
              <ViewAllBtn onClick={handleSearchSubmit}>
                مشاهده همه نتایج برای «{query}»
              </ViewAllBtn>
            </>
          ) : (
            <LoadingText>محصولی یافت نشد!</LoadingText>
          )}
        </Dropdown>
      )}
    </SearchContainer>
  );
}