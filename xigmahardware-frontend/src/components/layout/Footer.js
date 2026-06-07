// src/components/layout/Footer.js
'use client';

import styled from '@emotion/styled';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import {
  faStore, faPhone, faEnvelope, faMapMarkerAlt,
  faPaperPlane, faShieldAlt, faTruck, faHeadset,
  faMoneyBillWave
} from '@fortawesome/free-solid-svg-icons';
import { faInstagram, faTelegram, faTwitter, faLinkedin } from '@fortawesome/free-brands-svg-icons';

const FooterWrapper = styled.footer`
  background: ${props => props.theme.colors.bg.dark};
  color: white;
  margin-top: 80px;
`;

const Features = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 48px 24px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  border-bottom: 1px solid rgba(255,255,255,0.1);

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
`;

const FeatureItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  color: rgba(255,255,255,0.8);
  font-size: 0.9rem;

  .icon {
    font-size: 2rem;
    color: ${props => props.theme.colors.primary[400]};
  }

  strong {
    display: block;
    color: white;
    margin-bottom: 4px;
  }
`;

const MainFooter = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 48px 24px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FooterColumn = styled.div`
  h3 {
    color: white;
    font-size: 1.1rem;
    margin-bottom: 20px;
    font-weight: 600;
  }

  ul {
    list-style: none;
  }

  li {
    margin-bottom: 12px;
  }

  a {
    color: rgba(255,255,255,0.6);
    font-size: 0.9rem;
    transition: color 0.2s;
    text-decoration: none;

    &:hover {
      color: ${props => props.theme.colors.primary[400]};
    }
  }
`;

const BrandSection = styled.div`
  p {
    color: rgba(255,255,255,0.6);
    font-size: 0.9rem;
    line-height: 1.8;
    margin: 16px 0;
  }
`;

const Newsletter = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;

  input {
    flex: 1;
    padding: 12px 16px;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: ${props => props.theme.borderRadius.md};
    background: rgba(255,255,255,0.05);
    color: white;
    font-family: ${props => props.theme.fonts.primary};
    outline: none;

    &:focus {
      border-color: ${props => props.theme.colors.primary[500]};
    }
  }

  button {
    padding: 12px 20px;
    background: ${props => props.theme.colors.primary[500]};
    color: white;
    border: none;
    border-radius: ${props => props.theme.borderRadius.md};
    cursor: pointer;
  }
`;

const SocialIcons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;

  a {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    transition: all 0.3s;

    &:hover {
      background: ${props => props.theme.colors.primary[500]};
      transform: translateY(-2px);
    }
  }
`;

const Bottom = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 0.85rem;
  color: rgba(255,255,255,0.5);

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
`;

export const Footer = () => {
  return (
    <FooterWrapper>
      {/* Features Bar */}
      <Features>
        <FeatureItem>
          <Icon icon={faTruck} className="icon" size="xl" />
          <div>
            <strong>ارسال سریع</strong>
            <span>به سراسر ایران</span>
          </div>
        </FeatureItem>
        <FeatureItem>
          <Icon icon={faShieldAlt} className="icon" size="xl" />
          <div>
            <strong>ضمانت اصالت</strong>
            <span>کالای اورجینال</span>
          </div>
        </FeatureItem>
        <FeatureItem>
          <Icon icon={faHeadset} className="icon" size="xl" />
          <div>
            <strong>پشتیبانی ۲۴/۷</strong>
            <span>پاسخگویی آنلاین</span>
          </div>
        </FeatureItem>
        <FeatureItem>
          <Icon icon={faMoneyBillWave} className="icon" size="xl" />
          <div>
            <strong>قیمت رقابتی</strong>
            <span>بهترین قیمت بازار</span>
          </div>
        </FeatureItem>
      </Features>

      {/* Main Footer */}
      <MainFooter>
        <BrandSection>
          <h3>
            <Icon icon={faStore} size="lg" /> XigmaHardware
          </h3>
          <p>
            XigmaHardware بزرگترین marketplace سخت‌افزارهای سازمانی در ایران است.
            ما با ارائه بهترین محصولات از برندهای معتبر جهانی،
            راه‌حل‌های حرفه‌ای برای کسب‌وکار شما فراهم می‌کنیم.
          </p>
          <Newsletter>
            <input type="email" placeholder="ایمیل شما..." />
            <button>
              <Icon icon={faPaperPlane} size="sm" />
            </button>
          </Newsletter>
          <SocialIcons>
            <a href="#"><Icon icon={faInstagram} /></a>
            <a href="#"><Icon icon={faTelegram} /></a>
            <a href="#"><Icon icon={faTwitter} /></a>
            <a href="#"><Icon icon={faLinkedin} /></a>
          </SocialIcons>
        </BrandSection>

        <FooterColumn>
          <h3>دسترسی سریع</h3>
          <ul>
            <li><Link href="/products">محصولات</Link></li>
            <li><Link href="/brands">برندها</Link></li>
            <li><Link href="/products/featured">پیشنهاد ویژه</Link></li>
            <li><Link href="/products/bestsellers">پرفروش‌ترین‌ها</Link></li>
            <li><Link href="/articles">مقالات</Link></li>
          </ul>
        </FooterColumn>

        <FooterColumn>
          <h3>خدمات مشتریان</h3>
          <ul>
            <li><Link href="/dashboard">حساب کاربری</Link></li>
            <li><Link href="/dashboard/orders">پیگیری سفارش</Link></li>
            <li><Link href="/support">پشتیبانی</Link></li>
            <li><Link href="/faq">سوالات متداول</Link></li>
            <li><Link href="/warranty">گارانتی</Link></li>
          </ul>
        </FooterColumn>

        <FooterColumn>
          <h3>تماس با ما</h3>
          <ul>
            <li><Icon icon={faPhone} size="sm" /> ۰۲۱-۱۲۳۴۵۶۷۸</li>
            <li><Icon icon={faEnvelope} size="sm" /> info@xigmahardware.com</li>
            <li><Icon icon={faMapMarkerAlt} size="sm" /> تهران، خیابان ولیعصر</li>
          </ul>
        </FooterColumn>
      </MainFooter>

      <Bottom>
        <span>© ۲۰۲۶ XigmaHardware. تمامی حقوق محفوظ است.</span>
        <span>طراحی و توسعه با ❤️ توسط تیم Xigma</span>
      </Bottom>
    </FooterWrapper>
  );
};