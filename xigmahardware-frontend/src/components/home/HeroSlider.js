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
  height: 480px;
  overflow: hidden;
  margin-top: 72px;

  @media (max-width: 768px) { height: 350px; }
  @media (max-width: 480px) { height: 280px; }
`;

const Slide = styled.div`
  position: absolute;
  inset: 0;
  opacity: ${p => p.$active ? 1 : 0};
  transform: translateX(${p => p.$active ? '0' : p.$dir === 'left' ? '-100%' : '100%'});
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, ${p => p.$from}, ${p => p.$to});
  display: flex;
  align-items: center;
  padding: 0 80px;

  @media (max-width: 768px) { padding: 0 40px; }
`;

const SlideContent = styled.div`
  flex: 1;
  color: white;
  animation: ${p => p.$active ? 'fadeInUp 0.6s ease-out 0.2s both' : 'none'};
`;

const SlideTag = styled.span`
  display: inline-block;
  padding: 6px 14px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 500;
  margin-bottom: 16px;
`;

const SlideTitle = styled.h2`
  font-size: 2.8rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 12px;
  letter-spacing: -1px;

  @media (max-width: 768px) { font-size: 1.6rem; }
`;

const SlideDesc = styled.p`
  font-size: 1.1rem;
  opacity: 0.85;
  margin-bottom: 24px;
  max-width: 480px;
  line-height: 1.7;

  @media (max-width: 768px) { font-size: 0.95rem; }
`;

const SlideEmoji = styled.div`
  font-size: 10rem;
  opacity: 0.7;
  animation: ${p => p.$active ? 'fadeIn 0.8s ease-out 0.4s both' : 'none'};

  @media (max-width: 768px) { display: none; }
`;

const NavBtn = styled.button`
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  ${p => p.$side === 'left' ? 'left: 20px;' : 'right: 20px;'}
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(8px);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 5;

  &:hover {
    background: rgba(255,255,255,0.25);
    transform: translateY(-50%) scale(1.05);
  }

  @media (max-width: 768px) {
    width: 36px; height: 36px;
    ${p => p.$side === 'left' ? 'left: 8px;' : 'right: 8px;'}
  }
`;

const Dots = styled.div`
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 5;
`;

const Dot = styled.button`
  width: ${p => p.$active ? 28 : 8}px;
  height: 8px;
  border-radius: 4px;
  border: none;
  background: ${p => p.$active ? 'white' : 'rgba(255,255,255,0.35)'};
  cursor: pointer;
  transition: all 0.3s;
`;

const slides = [
  {
    tag: '🆕 ورود جدید',
    title: 'سرورهای HP ProLiant Gen11',
    desc: 'قدرت پردازش نسل جدید با Intel Xeon Scalable | گارانتی ۳ ساله XigmaHardware',
    emoji: '🖥️',
    from: '#0f172a', to: '#5b21b6',
    link: '/products/hp-proliant-gen11',
  },
  {
    tag: '🔥 تخفیف ویژه',
    title: 'تا ۳۰٪ تخفیف Workstation',
    desc: 'Dell Precision با پردازنده‌های Xeon و حافظه ECC',
    emoji: '💻',
    from: '#1e293b', to: '#6d28d9',
    link: '/products/workstations',
  },
  {
    tag: '🌟 پرفروش',
    title: 'تجهیزات شبکه Cisco',
    desc: 'سوئیچ‌ها و روترهای سازمانی با گارانتی معتبر',
    emoji: '🌐',
    from: '#0f172a', to: '#4338ca',
    link: '/products/networking',
  },
  {
    tag: '💾 جدید',
    title: 'ذخیره‌سازهای NVMe',
    desc: 'SSD های سازمانی با سرعت ۷GB/s',
    emoji: '💾',
    from: '#1e293b', to: '#059669',
    link: '/products/storage',
  },
];

export const HeroSlider = () => {
  const [current, setCurrent] = useState(0);
  const [dir, setDir] = useState('right');
  const timer = useRef(null);

  const go = useCallback((i, d = 'right') => { setDir(d); setCurrent(i); }, []);
  const next = useCallback(() => { setDir('right'); setCurrent(p => (p + 1) % slides.length); }, []);
  const prev = useCallback(() => { setDir('left'); setCurrent(p => (p - 1 + slides.length) % slides.length); }, []);

  useEffect(() => {
    timer.current = setInterval(next, 5000);
    return () => clearInterval(timer.current);
  }, [next]);

  return (
    <SliderWrapper>
      {slides.map((s, i) => (
        <Slide key={i} $active={i === current} $dir={dir} $from={s.from} $to={s.to}>
          <SlideContent $active={i === current}>
            <SlideTag>{s.tag}</SlideTag>
            <SlideTitle>{s.title}</SlideTitle>
            <SlideDesc>{s.desc}</SlideDesc>
            <Button variant="secondary" size="lg" onClick={() => window.location.href = s.link}>
              مشاهده و خرید
            </Button>
          </SlideContent>
          <SlideEmoji $active={i === current}>{s.emoji}</SlideEmoji>
        </Slide>
      ))}

      <NavBtn $side="left" onClick={prev}><Icon icon={faChevronRight} size="lg" /></NavBtn>
      <NavBtn $side="right" onClick={next}><Icon icon={faChevronLeft} size="lg" /></NavBtn>

      <Dots>
        {slides.map((_, i) => (
          <Dot key={i} $active={i === current} onClick={() => go(i)} />
        ))}
      </Dots>
    </SliderWrapper>
  );
};