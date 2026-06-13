// src/components/home/Hero.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';
import Link from 'next/link';

// داده‌های تستی اسلایدها (بعداً می‌تونی از API هم بگیری)
const slidesData = [
  {
    id: 1,
    title: 'قدرت و سرعت بی‌نهایت',
    subtitle: 'از تجهیزات رادیویی و دیتاسنتر تا مدرن‌ترین قطعات PC و Workstation. تجهیزات خود را با گارانتی معتبر تهیه کنید.',
    buttonText: 'مشاهده سرورها',
    link: '/market?category=servers',
  },
  {
    id: 2,
    title: 'مدرن‌ترین تجهیزات شبکه',
    subtitle: 'تضمین پایداری و امنیت ارتباطات سازمان شما با سوئیچ‌ها و روترهای برندهای معتبر جهانی.',
    buttonText: 'تجهیزات شبکه',
    link: '/market?category=network',
  },
  {
    id: 3,
    title: 'سیستم‌های پردازش سنگین',
    subtitle: 'اسمبل تخصصی ورک‌استیشن‌ها برای رندرینگ، هوش مصنوعی و گیمینگ با بهترین کانفیگ بازار.',
    buttonText: 'سفارش سیستم',
    link: '/market?category=workstations',
  }
];

const fadeInUp = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const SliderContainer = styled.section`
  position: relative;
  height: 70vh;
  min-height: 500px;
  width: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: ${({ theme }) => theme.colors.background};
`;

const Slide = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: ${({ active }) => (active ? 1 : 0)};
  transition: opacity 1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;

  /* یک بک‌گراند گرادیانت داینامیک و جذاب برای تم سخت‌افزاری */
  background: radial-gradient(
    circle at center,
    ${({ theme }) => theme.colors.surface} 0%,
    ${({ theme }) => theme.colors.background} 100%
  );
`;

const SlideContent = styled.div`
  max-width: 800px;
  z-index: 10;
  /* وقتی اسلاید فعال میشه، انیمیشن محتوا دوباره اجرا میشه */
  animation: ${({ active }) => (active ? fadeInUp : 'none')} 0.8s ease-out forwards;
`;

const Title = styled.h1`
  font-size: 3.5rem;
  font-weight: 900;
  margin-bottom: 1rem;
  background: linear-gradient(90deg, ${({ theme }) => theme.colors.primary}, #60A5FA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;

  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: ${({ theme }) => theme.colors.textMuted};
  margin-bottom: 2rem;
  line-height: 1.8;
`;

const CTAButton = styled(Link)`
  display: inline-block;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff !important;
  padding: 1rem 2.5rem;
  font-size: 1.2rem;
  border-radius: 30px;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0, 86, 210, 0.4);
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 86, 210, 0.6);
  }
`;

const IndicatorsContainer = styled.div`
  position: absolute;
  bottom: 2rem;
  display: flex;
  gap: 10px;
  z-index: 20;
`;

const Dot = styled.button`
  width: ${({ active }) => (active ? '30px' : '10px')};
  height: 10px;
  border-radius: 5px;
  background-color: ${({ active, theme }) => (active ? theme.colors.primary : theme.colors.border)};
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background-color: ${({ theme }) => theme.colors.primary};
    opacity: 0.8;
  }
`;

export default function Hero() {
  const [currentSlide, setCurrentSlide] = useState(0);

  // افکت برای تغییر اتوماتیک اسلایدها هر 5 ثانیه
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev === slidesData.length - 1 ? 0 : prev + 1));
    }, 5000);

    // کلین‌آپ برای جلوگیری از نشت حافظه (Memory Leak)
    return () => clearInterval(timer);
  }, []);

  return (
    <SliderContainer>
      {slidesData.map((slide, index) => (
        <Slide key={slide.id} active={index === currentSlide}>
          <SlideContent active={index === currentSlide}>
            <Title>{slide.title}</Title>
            <Subtitle>{slide.subtitle}</Subtitle>
            <CTAButton href={slide.link}>{slide.buttonText}</CTAButton>
          </SlideContent>
        </Slide>
      ))}

      {/* نقطه‌های پایین اسلایدر */}
      <IndicatorsContainer>
        {slidesData.map((_, index) => (
          <Dot
            key={index}
            active={index === currentSlide}
            onClick={() => setCurrentSlide(index)}
            aria-label={`برو به اسلاید ${index + 1}`}
          />
        ))}
      </IndicatorsContainer>
    </SliderContainer>
  );
}