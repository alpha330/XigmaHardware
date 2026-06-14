// src/components/support/LiveChatWidget.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../utils/apiFetch';

// ================= STYLES =================
const WidgetContainer = styled.div`
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
`;

const ToggleButton = styled.button`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  transition: transform 0.3s;

  &:hover { transform: scale(1.05); }
`;

const ChatWindow = styled.div`
  width: 350px;
  height: 500px;
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform-origin: bottom right;
  transition: opacity 0.3s, transform 0.3s;

  /* انیمیشن باز و بسته شدن */
  opacity: ${({ isOpen }) => (isOpen ? 1 : 0)};
  transform: ${({ isOpen }) => (isOpen ? 'scale(1)' : 'scale(0)')};
  pointer-events: ${({ isOpen }) => (isOpen ? 'auto' : 'none')};

  @media (max-width: 400px) {
    width: calc(100vw - 2rem);
    height: 60vh;
    right: 1rem;
    bottom: 5rem;
  }
`;

const Header = styled.div`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title { font-weight: bold; display: flex; align-items: center; gap: 0.5rem; }
  .close { background: none; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; }
`;

const MessagesArea = styled.div`
  flex: 1;
  padding: 1rem;
  background-color: ${({ theme }) => theme.colors.background};
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const Bubble = styled.div`
  max-width: 85%;
  padding: 0.8rem 1rem;
  border-radius: ${({ isSelf }) => (isSelf ? '12px 12px 0 12px' : '12px 12px 12px 0')};
  background-color: ${({ theme, isSelf }) => (isSelf ? theme.colors.primary : theme.colors.surface)};
  color: ${({ theme, isSelf }) => (isSelf ? '#fff' : theme.colors.textMain)};
  border: 1px solid ${({ theme, isSelf }) => (isSelf ? theme.colors.primary : theme.colors.border)};
  align-self: ${({ isSelf }) => (isSelf ? 'flex-end' : 'flex-start')};
  font-size: 0.9rem;
  line-height: 1.5;
  word-wrap: break-word;
`;

const InputArea = styled.form`
  display: flex;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
  background-color: ${({ theme }) => theme.colors.surface};
  padding: 0.5rem;
`;

const Input = styled.input`
  flex: 1;
  border: none;
  background: none;
  padding: 0.8rem;
  color: ${({ theme }) => theme.colors.textMain};
  outline: none;
  font-family: inherit;
`;

const SendBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0 1rem;
  cursor: pointer;
  font-weight: bold;
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

// --- Start Form Styles ---
const StartForm = styled.form`
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
  background-color: ${({ theme }) => theme.colors.background};

  h3 { color: ${({ theme }) => theme.colors.textMain}; text-align: center; margin-bottom: 1rem; }
  label { font-size: 0.85rem; color: ${({ theme }) => theme.colors.textMuted}; font-weight: bold; }
  input, textarea {
    width: 100%; padding: 0.8rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
    background-color: ${({ theme }) => theme.colors.surface}; color: ${({ theme }) => theme.colors.textMain};
    font-family: inherit; outline: none;
    &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
  }
  textarea { resize: none; height: 80px; }
  button {
    background-color: ${({ theme }) => theme.colors.success}; color: #fff; border: none; padding: 1rem;
    border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 1rem;
  }
`;

export default function LiveChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState('');

  // فرم شروع چت
  const [startData, setStartData] = useState({ subject: '', message: '' });

  const messagesEndRef = useRef(null);
  const pollingInterval = useRef(null);

  // اسکرول خودکار به پایین
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // دریافت اطلاعات سشن فعال و پیام‌ها
  const fetchSession = async (sessionId) => {
    try {
      const res = await apiFetch(`/api/v1/support/chats/${sessionId}/`);
      if (res.ok) {
        const data = await res.json();
        setSession(data);
        if (data.messages) {
          setMessages(data.messages);
        }
      }
    } catch (error) {
      console.error('Failed to fetch chat session');
    }
  };

  // چک کردن اینکه آیا از قبل چت فعالی داریم یا نه
  useEffect(() => {
    const checkActiveChats = async () => {
      try {
        const res = await apiFetch('/api/v1/support/chats/');
        if (res.ok) {
          const data = await res.json();
          const list = data.results || data;
          // پیدا کردن سشنی که هنوز باز است
          const activeSession = list.find(s => s.status === 'waiting' || s.status === 'active');
          if (activeSession) {
            setSession(activeSession);
            fetchSession(activeSession.id);
          }
        }
      } catch (error) {
        // نادیده گرفتن خطا در صورتی که کاربر لاگین نیست
      }
    };

    if (isOpen && !session) {
      checkActiveChats();
    }
  }, [isOpen]);

  // راه‌اندازی Polling برای دریافت پیام‌های جدید
  useEffect(() => {
    if (isOpen && session && session.status !== 'closed') {
      pollingInterval.current = setInterval(() => {
        fetchSession(session.id);
      }, 5000); // هر 5 ثانیه بررسی می‌کند
    } else {
      clearInterval(pollingInterval.current);
    }

    return () => clearInterval(pollingInterval.current);
  }, [isOpen, session]);

  const handleStartChat = async (e) => {
    e.preventDefault();
    if (!startData.subject || !startData.message) return;
    setLoading(true);

    try {
      const res = await apiFetch('/api/v1/support/chats/start/', {
        method: 'POST',
        body: JSON.stringify(startData),
      });
      const data = await res.json();
      if (res.ok) {
        setSession(data);
        setStartData({ subject: '', message: '' });
        fetchSession(data.id);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!text.trim() || !session) return;

    // اضافه کردن موقت به UI برای سرعت حس کاربری
    const tempMsg = { id: Date.now(), message: text, is_sender: true };
    setMessages(prev => [...prev, tempMsg]);
    setText('');

    try {
      await apiFetch(`/api/v1/support/chats/${session.id}/send/`, {
        method: 'POST',
        body: JSON.stringify({ message: tempMsg.message }),
      });
      fetchSession(session.id); // آپدیت نهایی از سرور
    } catch (error) {
      console.error(error);
    }
  };

  const handleCloseChat = async () => {
    if (!session) return setIsOpen(false);

    const confirmClose = window.confirm('آیا می‌خواهید به این گفتگو پایان دهید؟');
    if (!confirmClose) return;

    try {
      await apiFetch(`/api/v1/support/chats/${session.id}/close/`, { method: 'POST' });
      setSession(null);
      setMessages([]);
      setIsOpen(false);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <WidgetContainer>
      <ChatWindow isOpen={isOpen}>
        <Header>
          <div className="title">🎧 پشتیبانی آنلاین</div>
          <button className="close" onClick={() => setIsOpen(false)}>✖</button>
        </Header>

        {!session ? (
          <StartForm onSubmit={handleStartChat}>
            <h3>شروع گفتگوی جدید</h3>
            <div>
              <label>موضوع</label>
              <input
                required
                placeholder="مثلا: مشکل در پرداخت"
                value={startData.subject}
                onChange={e => setStartData({...startData, subject: e.target.value})}
              />
            </div>
            <div>
              <label>پیام شما</label>
              <textarea
                required
                placeholder="سوال خود را بپرسید..."
                value={startData.message}
                onChange={e => setStartData({...startData, message: e.target.value})}
              />
            </div>
            <button type="submit" disabled={loading}>
              {loading ? 'کمی صبر کنید...' : 'شروع چت'}
            </button>
          </StartForm>
        ) : (
          <>
            <MessagesArea>
              {session.status === 'closed' && (
                <div style={{ textAlign: 'center', color: 'var(--textMuted)', fontSize: '0.85rem' }}>
                  این گفتگو پایان یافته است.
                </div>
              )}
              {messages.map((msg, idx) => {
                // اگر بک‌اند در سریالایزر فیلد is_sender یا نوع فرستنده را می‌فرستد از آن استفاده کنید.
                // در اینجا فرض کردیم پیام‌های خود کاربر is_sender=true هستند.
                const isSelf = msg.is_sender !== false;
                return (
                  <Bubble key={msg.id || idx} isSelf={isSelf}>
                    {msg.message}
                  </Bubble>
                );
              })}
              <div ref={messagesEndRef} />
            </MessagesArea>

            {session.status !== 'closed' && (
              <InputArea onSubmit={handleSendMessage}>
                <Input
                  placeholder="پیام خود را بنویسید..."
                  value={text}
                  onChange={e => setText(e.target.value)}
                />
                <SendBtn type="submit" disabled={!text.trim()}>ارسال</SendBtn>
              </InputArea>
            )}

            {session.status !== 'closed' && (
              <div style={{ padding: '0.5rem', backgroundColor: 'var(--background)', textAlign: 'center' }}>
                <button
                  onClick={handleCloseChat}
                  style={{ background: 'none', border: 'none', color: 'var(--error)', fontSize: '0.8rem', cursor: 'pointer', fontWeight: 'bold' }}>
                  پایان دادن به چت
                </button>
              </div>
            )}
          </>
        )}
      </ChatWindow>

      <ToggleButton onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '✖' : '💬'}
      </ToggleButton>
    </WidgetContainer>
  );
}