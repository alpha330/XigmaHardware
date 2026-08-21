'use client';

import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import CircularTimer from './CircularTimer';

const InputContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: clamp(6px, 2vw, 10px);
  margin: 1rem 0;
  direction: ltr;
`;

const SingleInput = styled.input`
  width: clamp(38px, 10vw, 48px);
  height: 56px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  background: ${({ theme }) => theme.colors.inputBackground};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0;
  outline: none;
  caret-color: ${({ theme }) => theme.colors.primary};
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.borderStrong};
  }

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 4px ${({ theme }) => theme.colors.focusRing};
  }
`;

const TimerArea = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1.5rem;
`;

const ResendButton = styled.button`
  padding: 0.7rem 1.25rem;
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 10px;
  background: transparent;
  color: ${({ theme }) => theme.colors.primary};
  cursor: pointer;
  font-weight: 800;
  transition: color 0.2s ease, background-color 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryLight};
  }
`;

export default function OTPInput({ length = 6, onComplete, resendOTP }) {
  const [otp, setOtp] = useState(new Array(length).fill(""));
  const [timer, setTimer] = useState(120);
  const inputRefs = useRef([]);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

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
    if (code.length === length) onCompleteRef.current(code);
  }, [otp, length]);

  return (
    <div>
      <InputContainer>
        {otp.map((data, index) => (
          <SingleInput
            key={index}
            type="text"
            inputMode="numeric"
            autoComplete={index === 0 ? 'one-time-code' : 'off'}
            aria-label={`رقم ${index + 1} کد تایید`}
            maxLength={6}
            value={data}
            onChange={(e) => handleChange(e, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            ref={(el) => (inputRefs.current[index] = el)}
          />
        ))}
      </InputContainer>
      <TimerArea>
        {timer > 0 ? (
          <CircularTimer timeLeft={timer} />
        ) : (
          <ResendButton
            type="button"
            onClick={() => { setTimer(120); resendOTP(); }}
          >
            ارسال مجدد کد
          </ResendButton>
        )}
      </TimerArea>
    </div>
  );
}
