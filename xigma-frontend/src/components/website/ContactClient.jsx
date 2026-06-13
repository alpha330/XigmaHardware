// src/components/website/ContactClient.jsx
'use client';

import React, { useState } from 'react';
import styled from '@emotion/styled';
import { keyframes } from '@emotion/react';

const fadeInUp = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const PageWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
  animation: ${fadeInUp} 0.8s ease-out forwards;
`;

const HeaderSection = styled.div`
  text-align: center;
  margin-bottom: 4rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 900;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 1rem;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMuted};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const InfoBox = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 1rem;

  div {
    display: flex;
    flex-direction: column;
  }

  h4 {
    color: ${({ theme }) => theme.colors.textMain};
    margin-bottom: 0.3rem;
  }

  p {
    color: ${({ theme }) => theme.colors.textMuted};
    line-height: 1.6;
  }
`;

const IconWrapper = styled.div`
  font-size: 1.8rem;
  background-color: ${({ theme }) => `${theme.colors.primary}15`};
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const FormBox = styled.form`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  color: ${({ theme }) => theme.colors.textMain};
  font-weight: bold;
  font-size: 0.9rem;
`;

const Input = styled.input`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  transition: all 0.2s ease;
  outline: none;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => `${theme.colors.primary}33`};
  }
`;

const TextArea = styled.textarea`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  color: ${({ theme }) => theme.colors.textMain};
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-family: inherit;
  min-height: 150px;
  resize: vertical;
  transition: all 0.2s ease;
  outline: none;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 3px ${({ theme }) => `${theme.colors.primary}33`};
  }
`;

const SubmitButton = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  margin-top: 1rem;

  &:hover {
    background-color: ${({ theme }) => theme.colors.secondary};
    transform: translateY(-2px);
  }

  &:disabled {
    background-color: ${({ theme }) => theme.colors.border};
    cursor: not-allowed;
    transform: none;
  }
`;

const AlertMessage = styled.div`
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  background-color: ${({ type, theme }) => type === 'success' ? `${theme.colors.success}20` : `${theme.colors.error}20`};
  color: ${({ type, theme }) => type === 'success' ? theme.colors.success : theme.colors.error};
  border: 1px solid ${({ type, theme }) => type === 'success' ? theme.colors.success : theme.colors.error};
`;

export default function ContactClient() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });

  const [status, setStatus] = useState({ loading: false, type: null, message: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ loading: true, type: null, message: '' });

    try {
      const res = await fetch('http://localhost:8000/api/v1/website/contact/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!res.ok) throw new Error('خطا در ارسال پیام');

      setStatus({
        loading: false,
        type: 'success',
        message: 'پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس خواهیم گرفت.'
      });

      // پاک کردن فرم بعد از ارسال موفق
      setFormData({ name: '', email: '', phone: '', subject: '', message: '' });

    } catch (error) {
      console.error(error);
      setStatus({
        loading: false,
        type: 'error',
        message: 'متاسفانه مشکلی در ارسال پیام به وجود آمد. لطفا مجددا تلاش کنید.'
      });
    }
  };

  return (
    <PageWrapper>
      <HeaderSection>
        <Title>ارتباط با ما</Title>
        <Subtitle>خوشحال می‌شویم صدای شما را بشنویم. برای مشاوره، پشتیبانی یا ثبت شکایات با ما در تماس باشید.</Subtitle>
      </HeaderSection>

      <Grid>
        {/* اطلاعات تماس */}
        <InfoBox>
          <InfoItem>
            <IconWrapper>📍</IconWrapper>
            <div>
              <h4>آدرس دفتر مرکزی</h4>
              <p>تهران، خیابان ولیعصر، بالاتر از میدان ونک، برج فناوری زیگما، طبقه دهم</p>
            </div>
          </InfoItem>

          <InfoItem>
            <IconWrapper>📞</IconWrapper>
            <div>
              <h4>تلفن تماس</h4>
              <p dir="ltr">+98 21 1234 5678</p>
              <p dir="ltr">+98 912 345 6789</p>
            </div>
          </InfoItem>

          <InfoItem>
            <IconWrapper>✉️</IconWrapper>
            <div>
              <h4>ایمیل سازمانی</h4>
              <p dir="ltr">info@xigmahardware.com</p>
              <p dir="ltr">support@xigmahardware.com</p>
            </div>
          </InfoItem>

          <InfoItem>
            <IconWrapper>🕒</IconWrapper>
            <div>
              <h4>ساعات کاری</h4>
              <p>شنبه تا چهارشنبه: ۹ صبح الی ۱۸ عصر</p>
              <p>پنج‌شنبه‌ها: ۹ صبح الی ۱۴ ظهر</p>
            </div>
          </InfoItem>
        </InfoBox>

        {/* فرم تماس */}
        <FormBox onSubmit={handleSubmit}>
          {status.message && (
            <AlertMessage type={status.type}>{status.message}</AlertMessage>
          )}

          <InputGroup>
            <Label htmlFor="name">نام و نام خانوادگی</Label>
            <Input
              type="text"
              id="name"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
            />
          </InputGroup>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <InputGroup>
              <Label htmlFor="email">ایمیل</Label>
              <Input
                type="email"
                id="email"
                name="email"
                dir="ltr"
                required
                value={formData.email}
                onChange={handleChange}
              />
            </InputGroup>
            <InputGroup>
              <Label htmlFor="phone">شماره موبایل</Label>
              <Input
                type="tel"
                id="phone"
                name="phone"
                dir="ltr"
                required
                value={formData.phone}
                onChange={handleChange}
              />
            </InputGroup>
          </div>

          <InputGroup>
            <Label htmlFor="subject">موضوع پیام</Label>
            <Input
              type="text"
              id="subject"
              name="subject"
              required
              value={formData.subject}
              onChange={handleChange}
            />
          </InputGroup>

          <InputGroup>
            <Label htmlFor="message">متن پیام</Label>
            <TextArea
              id="message"
              name="message"
              required
              value={formData.message}
              onChange={handleChange}
              placeholder="لطفا توضیحات خود را اینجا بنویسید..."
            />
          </InputGroup>

          <SubmitButton type="submit" disabled={status.loading}>
            {status.loading ? 'در حال ارسال...' : 'ارسال پیام'}
          </SubmitButton>
        </FormBox>
      </Grid>
    </PageWrapper>
  );
}