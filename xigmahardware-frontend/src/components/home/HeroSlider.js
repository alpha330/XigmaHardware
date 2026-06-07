// src/components/home/HeroSlider.js
'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { Button } from '@/components/ui/Button';
import { faChevronLeft, faChevronRight } from '@fortawesome/free-solid-svg-icons';

const SliderWrapper = styled.div`
  position: relative;
  width: 100%;
  height: 500px;
  overflow: hidden;
  margin-top: 120px;

  @media (max-width: 768px) {
    height: 350px;
    margin-top: 100px;
  }
`;

const Slide = styled.div`
  position: absolute;
  inset: 0;
  opacity: ${props => props.$active ? 1 : 0};
  transform: translateX(${props => props.$active ? '0' : props.$direction === 'left' ? '-100%' : '100%'});
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg,
    ${props => props.$color1 || props.theme.colors.primary[800]},
    ${props => props.$color2 || props.theme.colors.primary[600]}
  );
  display: flex;
  align-items: center;
  padding: 0 80px;

  @media (max-width: 768px) {
    padding: 0 40px;
  }
`;

const SlideContent = styled.div`
  flex: 1;
  color: white;
  animation: ${props => props.$active ? 'slideUp 0.6s ease-out' : 'none'};
`;

const SlideTitle = styled.h2`
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 16px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`;

const SlideSubtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 24px;
  max-width: 500px;
`;

const SlideImage = styled.div`
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12rem;
  opacity: 0.8;
  animation: ${props => props.$active ? 'fadeIn 0.8s ease-out' : 'none'};

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavButton = styled.button`
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  ${props => props.$side === 'left' ? 'left: 20px;' : 'right: 20px;'}
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  color: white;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.3s;
  z-index: 10;

  &:hover {
    background: rgba(255,255,255,0.4);
    transform: translateY(-50%) scale(1.1);
  }
`;

const Dots = styled.div`
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 10;
`;

const Dot = styled.button`
  width: ${props => props.$active ? '32px' : '10px'};
  height: 10px;
  border-radius: 5px;
  border: none;
  background: ${props => props.$active ? 'white' : 'rgba(255,255,255,0.4)'};
  cursor: pointer;
  transition: all 0.3s;
`;

const slides = [
  {
    title: 'سرورهای HP ProLiant G10',
    subtitle: 'قدرت پردازش بی‌نظیر برای دیتاسنتر شما | با گارانتی ۳ ساله',
    color1: '#1a1a2e',
    color2: '#6b21a8',
    emoji: '🖥️',
    link: '/products/hp-proliant-g10',
  },
  {
    title: 'تخفیف ویژه Workstation',
    subtitle: 'تا ۳۰٪ تخفیف برای workstation های Dell Precision',
    color1: '#0f172a',
    color2: '#7e22ce',
    emoji: '💻',
    link: '/products/workstation',
  },
  {
    title: 'تجهیزات شبکه Cisco',
    subtitle: 'سوئیچ‌ها و روترهای سازمانی با بهترین قیمت',
    color1: '#1e293b',
    color2: '#4338ca',
    emoji: '🌐',
    link: '/products/network',
  },
  {
    title: 'ذخیره‌سازهای QNAP',
    subtitle: 'راه‌حل‌های ذخیره‌سازی NAS برای سازمان شما',
    color1: '#1a1a2e',
    color2: '#059669',
    emoji: '💾',
    link: '/products/storage',
  },
];

export const HeroSlider = () => {
  const [current, setCurrent] = useState(0);
  const [direction, setDirection] = useState('right');
  const timerRef = useRef(null);

  const goTo = useCallback((index, dir = 'right') => {
    setDirection(dir);
    setCurrent(index);
  }, []);

  const next = useCallback(() => {
    setDirection('right');
    setCurrent(prev => (prev + 1) % slides.length);
  }, []);

  const prev = useCallback(() => {
    setDirection('left');
    setCurrent(prev => (prev - 1 + slides.length) % slides.length);
  }, []);

  // Autoplay
  useEffect(() => {
    timerRef.current = setInterval(next, 5000);
    return () => clearInterval(timerRef.current);
  }, [next]);

  return (
    <SliderWrapper>
      {slides.map((slide, index) => (
        <Slide
          key={index}
          $active={index === current}
          $direction={direction}
          $color1={slide.color1}
          $color2={slide.color2}
        >
          <SlideContent $active={index === current}>
            <SlideTitle>{slide.title}</SlideTitle>
            <SlideSubtitle>{slide.subtitle}</SlideSubtitle>
            <Button variant="secondary" size="lg" onClick={() => window.location.href = slide.link}>
              مشاهده محصولات
            </Button>
          </SlideContent>
          <SlideImage $active={index === current}>
            {slide.emoji}
          </SlideImage>
        </Slide>
      ))}

      <NavButton $side="left" onClick={prev}>
        <Icon icon={faChevronRight} size="lg" />
      </NavButton>
      <NavButton $side="right" onClick={next}>
        <Icon icon={faChevronLeft} size="lg" />
      </NavButton>

      <Dots>
        {slides.map((_, index) => (
          <Dot
            key={index}
            $active={index === current}
            onClick={() => goTo(index)}
          />
        ))}
      </Dots>
    </SliderWrapper>
  );
};