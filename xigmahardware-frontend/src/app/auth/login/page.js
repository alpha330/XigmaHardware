// src/app/auth/login/page.js
'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { useToast } from '@/components/ui/Toast';
import { loginUser, requestOTP } from '@/lib/api';
import { setAuthCookies } from '@/lib/auth-actions';
import {
  faEnvelope, faMobile, faLock, faKey,
  faRightToBracket, faUserPlus, faQuestionCircle,
  faSun, faMoon, faStore, faCheck, faTimes,
  faSpinner
} from '@fortawesome/free-solid-svg-icons';

const PageWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.bg.dark} 0%,
    ${props => props.theme.colors.primary[900]} 100%
  );
  padding: 2rem;
  position: relative;
`;

const ThemeToggleWrapper = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
`;

const LoginCard = styled.div`
  width: 100%;
  max-width: 440px;
  background: ${props => props.theme.colors.card};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.xl};
  padding: 2.5rem;
  box-shadow: ${props => props.theme.shadows.xl};
  animation: slideUp 0.5s ease-out;
`;

const Logo = styled.div`
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg,
    ${props => props.theme.colors.primary[500]},
    ${props => props.theme.colors.primary[700]}
  );
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
  margin: 0 auto 1.5rem;
  box-shadow: ${props => props.theme.shadows.glow};
`;

const Title = styled.h1`
  font-size: ${props => props.theme.fontSizes['2xl']};
  font-weight: 700;
  text-align: center;
  color: ${props => props.theme.colors.text.primary};
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  text-align: center;
  color: ${props => props.theme.colors.text.muted};
  font-size: ${props => props.theme.fontSizes.sm};
  margin-bottom: 2rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
  color: ${props => props.theme.colors.text.muted};
  font-size: ${props => props.theme.fontSizes.sm};

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: ${props => props.theme.colors.border};
  }
`;

const TabButtons = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  background: ${props => props.theme.colors.gray[100]};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 4px;
`;

const TabButton = styled.button`
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: ${props => props.theme.borderRadius.sm};
  font-family: ${props => props.theme.fonts.primary};
  font-weight: ${props => props.$active ? 600 : 400};
  font-size: ${props => props.theme.fontSizes.sm};
  background: ${props => props.$active ? props.theme.colors.card : 'transparent'};
  color: ${props => props.$active ? props.theme.colors.primary[600] : props.theme.colors.text.secondary};
  cursor: pointer;
  transition: all ${props => props.theme.transitions.fast};
  box-shadow: ${props => props.$active ? props.theme.shadows.sm : 'none'};
`;

const FooterLinks = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  font-size: ${props => props.theme.fontSizes.sm};
`;

const FooterLink = styled(Link)`
  color: ${props => props.theme.colors.primary[500]};
  text-decoration: none;
  font-weight: 500;
  transition: color ${props => props.theme.transitions.fast};

  &:hover {
    color: ${props => props.theme.colors.primary[600]};
  }
`;

const ToggleOTPLink = styled.span`
  color: ${props => props.theme.colors.primary[500]};
  cursor: pointer;
  font-weight: 500;
  font-size: ${props => props.theme.fontSizes.sm};

  &:hover {
    color: ${props => props.theme.colors.primary[600]};
  }
`;

export default function LoginPage() {
  const toast = useToast();
  const [loginMethod, setLoginMethod] = useState('email');
  const [formData, setFormData] = useState({
    email: '',
    mobile: '',
    password: '',
    otpCode: '',
  });
  const [useOTP, setUseOTP] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // ✅ Server Action برای OTP
  const handleRequestOTP = async () => {
    if (!formData.mobile) {
      toast.warning('شماره موبایل را وارد کنید.');
      return;
    }

    const result = await requestOTP(formData.mobile);

    if (result.success) {
      toast.success('کد تایید ارسال شد 📱', 'ارسال موفق');
    } else {
      toast.error(result.error || 'خطا در ارسال کد');
    }
  };

  // ✅ Server Action برای Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    // اعتبارسنجی اولیه
    if (loginMethod === 'email' && !formData.email) {
      toast.warning('ایمیل را وارد کنید.');
      setLoading(false);
      return;
    }
    if (loginMethod === 'mobile' && !formData.mobile) {
      toast.warning('شماره موبایل را وارد کنید.');
      setLoading(false);
      return;
    }
    if (!useOTP && !formData.password) {
      toast.warning('رمز عبور را وارد کنید.');
      setLoading(false);
      return;
    }
    if (useOTP && !formData.otpCode) {
      toast.warning('کد تایید را وارد کنید.');
      setLoading(false);
      return;
    }

    // ✅ فراخوانی Server Action
    const result = await loginUser({
      email: loginMethod === 'email' ? formData.email : undefined,
      mobile: loginMethod === 'mobile' ? formData.mobile : undefined,
      password: !useOTP ? formData.password : undefined,
      otp_code: useOTP ? formData.otpCode : undefined,
    });

    if (result.success) {
      // ذخیره توکن‌ها در Cookie (Server Action)
      await setAuthCookies(
        result.data.tokens.access,
        result.data.tokens.refresh,
        result.data.user
      );

      toast.purple(`خوش آمدید ${result.data.user.first_name || 'کاربر'} عزیز! 🎉`, 'XigmaHardware');

      // ریدایرکت به داشبورد
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 800);
    } else {
      toast.error(result.error || 'اطلاعات وارد شده صحیح نیست.', 'خطا در ورود');
    }

    setLoading(false);
  };

  return (
    <PageWrapper>
      <ThemeToggleWrapper>
        <ThemeToggle />
      </ThemeToggleWrapper>

      <LoginCard>
        <Logo>🛒</Logo>
        <Title>ورود به XigmaHardware</Title>
        <Subtitle>قدرت سخت‌افزار، اعتماد شما</Subtitle>

        <TabButtons>
          <TabButton $active={loginMethod === 'email'} onClick={() => setLoginMethod('email')}>
            📧 ایمیل
          </TabButton>
          <TabButton $active={loginMethod === 'mobile'} onClick={() => setLoginMethod('mobile')}>
            📱 موبایل
          </TabButton>
        </TabButtons>

        <Form onSubmit={handleLogin}>
          {loginMethod === 'email' ? (
            <Input
              label="ایمیل"
              type="email"
              name="email"
              placeholder="example@email.com"
              value={formData.email}
              onChange={handleChange}
              icon={faEnvelope}       // ✅ FontAwesome
              ltr
            />
          ) : (
            <Input
              label="شماره موبایل"
              type="tel"
              name="mobile"
              placeholder="09123456789"
              value={formData.mobile}
              onChange={handleChange}
              icon={faMobile}          // ✅ FontAwesome
              ltr
            />
          )}

          {!useOTP ? (
            <Input
              label="رمز عبور"
              type="password"
              name="password"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              icon={faLock}            // ✅ FontAwesome
            />
          ) : (
            <Input
              label="کد تایید (OTP)"
              type="text"
              name="otpCode"
              placeholder="کد ۶ رقمی"
              value={formData.otpCode}
              onChange={handleChange}
              icon={faKey}             // ✅ FontAwesome
              ltr
            />
          )}

          <Button
            variant="primary"
            size="lg"
            fullWidth
            loading={loading}
            type="submit"
            icon={useOTP ? faKey : faRightToBracket}  // ✅ FontAwesome
          >
            {useOTP ? 'ورود با کد تایید' : 'ورود به حساب'}
          </Button>
        </Form>

        {loginMethod === 'mobile' && (
          <div style={{ textAlign: 'center', marginTop: '1rem' }}>
            <ToggleOTPLink
              onClick={() => {
                setUseOTP(!useOTP);
                if (!useOTP) handleRequestOTP();
              }}
            >
              {useOTP ? 'ورود با رمز عبور' : 'ورود با کد یکبار مصرف'}
            </ToggleOTPLink>
          </div>
        )}

        <Divider>یا</Divider>

        <FooterLinks>
          <FooterLink href="/auth/register">📝 ثبت‌نام</FooterLink>
          <FooterLink href="/auth/forgot-password">🔑 فراموشی رمز</FooterLink>
        </FooterLinks>
      </LoginCard>
    </PageWrapper>
  );
}