'use client';

import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import CircularTimer from './CircularTimer';

const InputContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 1rem 0;
  direction: ltr; /* مهم برای ترتیب درست اینپوت‌ها */
`;

const SingleInput = styled.input`
  width: 45px;
  height: 55px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 8px;
  background: ${({ theme }) => theme.colors.background};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0;
  outline: none;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 2px ${({ theme }) => theme.colors.primary}33;
  }
`;

export default function OTPInput({ length = 6, onComplete, resendOTP }) {
  const [otp, setOtp] = useState(new Array(length).fill(""));
  const [timer, setTimer] = useState(120);
  const inputRefs = useRef([]);

  // فوکوس روی اینپوت اول در شروع
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1); // 🎯 استفاده از Functional Update برای جلوگیری از باگ وابستگی
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  const handleChange = (e, index) => {
    const value = e.target.value;
    if (isNaN(value)) return;

    const newOtp = [...otp];

    // مدیریت Paste
    if (value.length > 1) {
      const pasted = value.slice(0, length).split("");
      pasted.forEach((char, i) => {
        if (index + i < length) newOtp[index + i] = char;
      });
      setOtp(newOtp);
      // انتقال فوکوس به آخرین اینپوت پر شده
      const lastIndex = Math.min(index + pasted.length - 1, length - 1);
      inputRefs.current[lastIndex].focus();
    } else {
      // حالت عادی تایپ یک کاراکتر
      newOtp[index] = value;
      setOtp(newOtp);

      // حرکت خودکار به جلو
      if (value !== "" && index < length - 1) {
        inputRefs.current[index + 1].focus();
      }
    }
  };

  const handleKeyDown = (e, index) => {
    // حرکت به عقب با Backspace
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1].focus();
    }
  };

  useEffect(() => {
    const code = otp.join("");
    if (code.length === length) onComplete(code);
  }, [otp]);

  return (
    <div>
      <InputContainer>
        {otp.map((data, index) => (
          <SingleInput
            key={index}
            type="text"
            maxLength={6} // برای اینکه Paste راحت عمل کند
            value={data}
            onChange={(e) => handleChange(e, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            ref={(el) => (inputRefs.current[index] = el)}
          />
        ))}
      </InputContainer>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '1.5rem' }}>
        {timer > 0 ? (
          <CircularTimer timeLeft={timer} />
        ) : (
          <button
            onClick={() => { setTimer(120); resendOTP(); }}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid var(--primary)',
              background: 'transparent',
              color: 'var(--primary)',
              cursor: 'pointer',
              fontWeight: 'bold',
              transition: '0.3s'
            }}
            onMouseOver={(e) => e.target.style.background = 'var(--primary-light)'}
            onMouseOut={(e) => e.target.style.background = 'transparent'}
          >
            ارسال مجدد کد
          </button>
        )}
      </div>
    </div>
  );
}