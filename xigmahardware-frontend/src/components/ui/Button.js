// src/components/ui/Button.js
'use client';

import styled from '@emotion/styled';
import { css } from '@emotion/react';
import { Icon } from './Icon';

const sizeStyles = {
  sm: css`padding: 6px 14px; font-size: 0.8rem; gap: 6px;`,
  md: css`padding: 10px 22px; font-size: 0.9rem; gap: 8px;`,
  lg: css`padding: 14px 30px; font-size: 1.05rem; gap: 10px;`,
};

const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-family: ${props => props.theme.fonts.primary};
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: ${props => props.$fullWidth ? '100%' : 'auto'};
  opacity: ${props => props.disabled ? 0.6 : 1};
  pointer-events: ${props => props.disabled ? 'none' : 'auto'};

  ${props => sizeStyles[props.$size || 'md']}

  ${props => {
    const { colors, shadows } = props.theme;
    switch (props.$variant) {
      case 'primary':
        return css`
          background: linear-gradient(135deg, ${colors.primary[500]}, ${colors.primary[700]});
          color: white;
          box-shadow: ${shadows.md};
          &:hover { box-shadow: ${shadows.lg}; transform: translateY(-2px); }
        `;
      case 'secondary':
        return css`
          background: ${colors.gray[100]};
          color: ${colors.text.primary};
          &:hover { background: ${colors.gray[200]}; }
        `;
      case 'outline':
        return css`
          border: 2px solid ${colors.primary[500]};
          color: ${colors.primary[500]};
          background: transparent;
          &:hover { background: ${colors.primary[50]}; }
        `;
      case 'ghost':
        return css`
          color: ${colors.primary[500]};
          background: transparent;
          &:hover { background: ${colors.primary[50]}; }
        `;
      case 'danger':
        return css`
          background: ${colors.danger};
          color: white;
          &:hover { filter: brightness(0.9); }
        `;
      default:
        return css``;
    }
  }}

  &:active { transform: scale(0.97); }
`;

export const Button = ({
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  icon,           // ✅ FontAwesome icon
  children,
  onClick,
  className,
}) => {
  return (
    <StyledButton
      $variant={variant}
      $size={size}
      $fullWidth={fullWidth}
      disabled={disabled || loading}
      onClick={onClick}
      className={className}
    >
      {loading ? (
        <Icon icon="spinner" size={size === 'sm' ? 'sm' : 'md'} pulse />
      ) : icon ? (
        <Icon icon={icon} size={size === 'sm' ? 'sm' : 'md'} />
      ) : null}
      {children}
    </StyledButton>
  );
};