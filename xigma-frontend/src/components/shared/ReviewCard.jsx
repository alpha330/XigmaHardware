// src/components/shared/ReviewCard.jsx
'use client';

import React from 'react';
import styled from '@emotion/styled';

const Card = styled.div`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  height: 100%;

  &:hover {
    border-color: ${({ theme }) => theme.colors.secondary};
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
`;

const UserName = styled.span`
  color: ${({ theme }) => theme.colors.textMain};
  font-weight: bold;
`;

const Rating = styled.div`
  color: #F59E0B; /* رنگ زرد ستاره */
  font-size: 1.2rem;
`;

const Body = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.95rem;
  line-height: 1.6;
`;

export default function ReviewCard({ review }) {
  return (
    <Card>
      <Header>
        <UserInfo>
          <Avatar>{review.user_name?.charAt(0) || 'U'}</Avatar>
          <UserName>{review.user_name || 'کاربر سایت'}</UserName>
        </UserInfo>
        <Rating>★★★★★</Rating>
      </Header>
      <h4 style={{ color: 'var(--textMain)', marginBottom: '0.5rem' }}>{review.title}</h4>
      <Body>{review.body}</Body>
    </Card>
  );
}