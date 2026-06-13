// src/components/shared/ExpertReviewCard.jsx
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
  position: relative;

  &:hover {
    transform: translateY(-5px);
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 10px 20px rgba(0, 86, 210, 0.15);
  }
`;

const Badge = styled.div`
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
  z-index: 10;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
`;

const ImageBox = styled.div`
  height: 200px;
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.background} 0%, ${({ theme }) => theme.colors.border} 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme.colors.textMuted};
  position: relative;
`;

const ScoreCircle = styled.div`
  position: absolute;
  bottom: -20px;
  left: 20px;
  width: 50px;
  height: 50px;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 3px solid ${({ theme }) => theme.colors.primary};
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
`;

const Content = styled.div`
  padding: 2rem 1.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const Title = styled.h3`
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.8rem;
  line-height: 1.4;
`;

const Excerpt = styled.p`
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

export default function ExpertReviewCard({ review }) {
  return (
    <Card href={`/expert-reviews/${review.id}`}>
      <Badge>Xigma Lab</Badge>
      <ImageBox>
        تصویر کالا
        <ScoreCircle>{review.expert_score || '9.5'}</ScoreCircle>
      </ImageBox>
      <Content>
        <Title>{review.title}</Title>
        <Excerpt>{review.summary}</Excerpt>
      </Content>
    </Card>
  );
}