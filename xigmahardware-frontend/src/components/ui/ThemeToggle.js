// src/components/ui/ThemeToggle.js
'use client';

import styled from '@emotion/styled';
import { useThemeMode } from '@/lib/ThemeContext';
import { faSun, faMoon } from '@fortawesome/free-solid-svg-icons';
import { Icon } from './Icon';

const ToggleButton = styled.button`
  width: 44px;
  height: 44px;
  border-radius: ${props => props.theme.borderRadius.md};
  border: 1px solid ${props => props.theme.colors.border};
  background: ${props => props.theme.colors.card};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all ${props => props.theme.transitions.fast};
  color: ${props => props.theme.colors.text.primary};

  &:hover {
    background: ${props => props.theme.colors.primary[50]};
    border-color: ${props => props.theme.colors.primary[500]};
    color: ${props => props.theme.colors.primary[500]};
  }
`;

export const ThemeToggle = () => {
  const themeContext = useThemeMode();

  // ✅ چک کن context وجود داره
  if (!themeContext) {
    return null;
  }

  const { toggleTheme, isDark } = themeContext;

  return (
    <ToggleButton
      onClick={toggleTheme}
      aria-label={isDark ? 'Light mode' : 'Dark mode'}
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      <Icon icon={isDark ? faSun : faMoon} size="md" />
    </ToggleButton>
  );
};