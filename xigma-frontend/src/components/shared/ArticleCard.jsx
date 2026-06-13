// src/components/shared/ArticleCard.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';

const Card = styled(Link)`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 10px 20px rgba(0, 86, 210, 0.1);
  }
`;

const ImageBox = styled.div`
  height: 180px;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.border} 0%, ${({ theme }) => theme.colors.background} 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Content = styled.div`
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const Title = styled.h3`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
`;

const Excerpt = styled.p`
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.6;
  margin-bottom: 1rem;
`;

const ReadMore = styled.span`
  margin-top: auto;
  font-weight: bold;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 0.9rem;
`;

export default function ArticleCard({ article }) {
  return (
    <Card href={`/news/${article.id}`}>
      <ImageBox>تصویر مقاله</ImageBox>
      <Content>
        <Title>{article.title}</Title>
        <Excerpt>{article.summary || 'خلاصه‌ای از این مقاله جذاب را در اینجا بخوانید...'}</Excerpt>
        <ReadMore>مطالعه کامل ←</ReadMore>
      </Content>
    </Card>
  );
}