// src/components/ui/Icon.js
'use client';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import styled from '@emotion/styled';

const IconWrapper = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  line-height: 1;

  // ✅ سایزهای دقیق‌تر
  &.icon-xs {
    font-size: 0.7rem;
    width: 0.7rem;
    height: 0.7rem;
  }
  &.icon-sm {
    font-size: 0.875rem;
    width: 0.875rem;
    height: 0.875rem;
  }
  &.icon-md {
    font-size: 1.1rem;
    width: 1.1rem;
    height: 1.1rem;
  }
  &.icon-lg {
    font-size: 1.4rem;
    width: 1.4rem;
    height: 1.4rem;
  }
  &.icon-xl {
    font-size: 1.8rem;
    width: 1.8rem;
    height: 1.8rem;
  }
  &.icon-2xl {
    font-size: 2.5rem;
    width: 2.5rem;
    height: 2.5rem;
  }
`;

export const Icon = ({ icon, size = 'md', color, className, pulse, ...props }) => {
  if (!icon) return null;

  return (
    <IconWrapper
      className={`icon-${size} ${className || ''}`}
      style={color ? { color } : {}}
    >
      <FontAwesomeIcon
        icon={icon}
        pulse={pulse}
        style={{ width: '100%', height: '100%' }}  // ✅ پر کردن container
        {...props}
      />
    </IconWrapper>
  );
};