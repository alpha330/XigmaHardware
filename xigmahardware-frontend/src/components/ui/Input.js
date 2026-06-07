// src/components/ui/Input.js
'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { css } from '@emotion/react';
import { Icon } from './Icon';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';

const InputWrapper = styled.div`
  position: relative;
  margin-bottom: 1.25rem;
`;

const StyledInput = styled.input`
  width: 100%;
  padding: 14px 16px;
  border: 2px solid ${props => props.$error ? props.theme.colors.danger : props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-family: ${props => props.theme.fonts.primary};
  font-size: ${props => props.theme.fontSizes.base};
  background: ${props => props.theme.colors.card};
  color: ${props => props.theme.colors.text.primary};
  transition: all ${props => props.theme.transitions.fast};
  outline: none;
  direction: ${props => props.$ltr ? 'ltr' : 'rtl'};

  &:focus {
    border-color: ${props => props.theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.primary[100]};
  }

  &::placeholder {
    color: ${props => props.theme.colors.text.muted};
    font-size: 0.9rem;
  }

  ${props => props.$hasIcon && css`
    padding-right: 48px;
  `}
`;

const Label = styled.label`
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  font-size: 0.9rem;
  color: ${props => props.theme.colors.text.secondary};
`;

const IconWrapper = styled.div`
  position: absolute;
  right: ${props => props.$right ? '16px' : 'auto'};
  left: ${props => props.$left ? '16px' : 'auto'};
  top: ${props => props.$hasLabel ? '44px' : '50%'};
  transform: translateY(-50%);
  color: ${props => props.theme.colors.text.muted};
  pointer-events: none;
`;

const TogglePassword = styled.button`
  position: absolute;
  left: 12px;
  top: ${props => props.$hasLabel ? '44px' : '50%'};
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: ${props => props.theme.colors.text.muted};
  padding: 4px;
  transition: color 0.2s;

  &:hover {
    color: ${props => props.theme.colors.primary[500]};
  }
`;

const ErrorText = styled.span`
  color: ${props => props.theme.colors.danger};
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
`;

export const Input = ({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  icon,           // ✅ این آیکون FontAwesome هست
  ltr = false,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

  return (
    <InputWrapper>
      {label && <Label>{label}</Label>}
      {icon && (
        <IconWrapper $hasLabel={!!label} $right={!ltr} $left={ltr}>
          <Icon icon={icon} size="sm" />  {/* ✅ اینجا icon رو به Icon کامپوننت میده */}
        </IconWrapper>
      )}
      <StyledInput
        type={inputType}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        $error={!!error}
        $hasIcon={!!icon}
        $ltr={ltr}
        $hasLabel={!!label}
        {...props}
      />
      {isPassword && (
        <TogglePassword
          type="button"
          $hasLabel={!!label}
          onClick={() => setShowPassword(!showPassword)}
        >
          <Icon icon={showPassword ? faEyeSlash : faEye} size="sm" />
        </TogglePassword>
      )}
      {error && <ErrorText>{error}</ErrorText>}
    </InputWrapper>
  );
};