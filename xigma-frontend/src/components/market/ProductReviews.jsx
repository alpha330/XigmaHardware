// src/components/market/ProductReviews.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../utils/apiFetch';
import { useToast } from '../ui/ToastProvider';

// ================= STYLES =================
const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`;

const StatsHeader = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  background-color: ${({ theme }) => theme.colors.background};
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const OverallScore = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border-left: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: 768px) {
    border-left: none;
    border-bottom: 1px solid ${({ theme }) => theme.colors.border};
    padding-bottom: 1rem;
  }

  .score { font-size: 3rem; font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; }
  .out-of { font-size: 1.2rem; color: ${({ theme }) => theme.colors.textMuted}; }
  .stars { color: #fbbf24; font-size: 1.5rem; margin: 0.5rem 0; }
  .count { font-size: 0.9rem; color: ${({ theme }) => theme.colors.textMuted}; }
`;

const BarsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;
`;

const BarRow = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: ${({ theme }) => theme.colors.textMain};

  .label { width: 120px; font-weight: bold; }
  .bar-bg { flex: 1; height: 8px; background-color: ${({ theme }) => theme.colors.border}; border-radius: 4px; overflow: hidden; }
  .bar-fill { height: 100%; background-color: ${({ theme }) => theme.colors.primary}; border-radius: 4px; }
  .value { width: 30px; text-align: left; font-weight: bold; }
`;

const ReviewCard = styled.div`
  padding: 1.5rem 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  &:last-child { border-bottom: none; }
`;

const ReviewHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;

  .user { font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; }
  .date { font-size: 0.85rem; color: ${({ theme }) => theme.colors.textMuted}; }
`;

const ReviewTitle = styled.h4`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textMain};
  margin-bottom: 0.5rem;
`;

const ReviewBody = styled.p`
  color: ${({ theme }) => theme.colors.textMuted};
  line-height: 1.6;
  font-size: 0.95rem;
  margin-bottom: 1rem;
`;

const ProsCons = styled.div`
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
  font-size: 0.9rem;

  @media (max-width: 600px) { flex-direction: column; gap: 0.5rem; }

  .list { display: flex; flex-direction: column; gap: 0.3rem; }
  .pro-item { color: ${({ theme }) => theme.colors.success}; display: flex; align-items: center; gap: 0.4rem; }
  .con-item { color: ${({ theme }) => theme.colors.error}; display: flex; align-items: center; gap: 0.4rem; }
`;

const AddReviewBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  align-self: flex-start;
  transition: opacity 0.2s;

  &:hover { opacity: 0.9; }
`;

// --- Form Styles ---
const FormContainer = styled.form`
  background-color: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
`;

const InputGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  label { font-size: 0.9rem; font-weight: bold; color: ${({ theme }) => theme.colors.textMain}; }
  input, textarea {
    background-color: ${({ theme }) => theme.colors.surface};
    border: 1px solid ${({ theme }) => theme.colors.border};
    color: ${({ theme }) => theme.colors.textMain};
    padding: 0.8rem; border-radius: 8px; font-family: inherit;
    &:focus { border-color: ${({ theme }) => theme.colors.primary}; outline: none; }
  }
  textarea { resize: vertical; min-height: 80px; }
`;

const ScoreGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;

  @media (max-width: 600px) { grid-template-columns: 1fr; }
`;

const SubmitBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.success};
  color: #fff; border: none; padding: 1rem; border-radius: 8px; font-weight: bold;
  cursor: pointer; margin-top: 1rem;
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

export default function ProductReviews({ productId, stats }) {
  const { showToast } = useToast();
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '', body: '', pros: '', cons: '',
    overall: 5, value_for_money: 5, quality: 5, performance: 5
  });

  const fetchReviews = async () => {
    try {
      const res = await apiFetch(`/api/v1/market/reviews/?product=${productId}`);
      if (res.ok) {
        const data = await res.json();
        setReviews(data.results || data);
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (productId) fetchReviews();
  }, [productId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    // آماده‌سازی دیتای فرم. (ساختار دقیق بستگی به ReviewSerializer شما در بک‌اند دارد)
    // معمولا یا rating به صورت Nested ارسال می‌شود، یا فیلدها مسطح ارسال می‌شوند.
    const payload = {
      product: productId,
      title: formData.title,
      body: formData.body,
      pros: formData.pros,
      cons: formData.cons,
      // اگر سریالایزر شما rating را جدا می‌گیرد:
      rating: {
        overall: formData.overall,
        value_for_money: formData.value_for_money,
        quality: formData.quality,
        performance: formData.performance,
      }
    };

    try {
      const res = await apiFetch('/api/v1/market/reviews/', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || err.detail || 'خطا در ثبت نظر. ممکن است قبلاً نظر داده باشید.');
      }

      showToast('نظر شما با موفقیت ثبت شد.', 'success');
      setShowForm(false);
      fetchReviews(); // رفرش لیست نظرات
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Container>
      {/* هدر آمار امتیازات */}
      <StatsHeader>
        <OverallScore>
          <div className="score">{stats.avg_rating || '۵.۰'}</div>
          <div className="stars">⭐⭐⭐⭐⭐</div>
          <div className="count">از مجموع {stats.rating_count || 0} رای</div>
        </OverallScore>

        <BarsContainer>
          <BarRow>
            <span className="label">ارزش خرید</span>
            <div className="bar-bg">
              <div className="bar-fill" style={{ width: `${((stats.avg_value_for_money || 5) / 5) * 100}%` }} />
            </div>
            <span className="value">{stats.avg_value_for_money || '۵.۰'}</span>
          </BarRow>
          <BarRow>
            <span className="label">کیفیت ساخت</span>
            <div className="bar-bg">
              <div className="bar-fill" style={{ width: `${((stats.avg_quality || 5) / 5) * 100}%` }} />
            </div>
            <span className="value">{stats.avg_quality || '۵.۰'}</span>
          </BarRow>
          <BarRow>
            <span className="label">عملکرد و کارایی</span>
            <div className="bar-bg">
              <div className="bar-fill" style={{ width: `${((stats.avg_performance || 5) / 5) * 100}%` }} />
            </div>
            <span className="value">{stats.avg_performance || '۵.۰'}</span>
          </BarRow>
        </BarsContainer>
      </StatsHeader>

      <AddReviewBtn onClick={() => setShowForm(!showForm)}>
        {showForm ? 'انصراف' : '✍️ ثبت نظر جدید'}
      </AddReviewBtn>

      {/* فرم ثبت نظر */}
      {showForm && (
        <FormContainer onSubmit={handleSubmit}>
          <h3>ثبت نظر و امتیاز</h3>
          <InputGroup>
            <label>عنوان نظر</label>
            <input required value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} placeholder="مثلاً: ارزش خرید بالا" />
          </InputGroup>
          <InputGroup>
            <label>متن نظر</label>
            <textarea required value={formData.body} onChange={e => setFormData({...formData, body: e.target.value})} placeholder="تجربه استفاده خود را بنویسید..." />
          </InputGroup>

          <ScoreGrid>
            <InputGroup>
              <label>نقاط قوت (هر مورد در یک خط)</label>
              <textarea value={formData.pros} onChange={e => setFormData({...formData, pros: e.target.value})} placeholder="صفحه نمایش عالی&#10;باتری قدرتمند" />
            </InputGroup>
            <InputGroup>
              <label>نقاط ضعف (هر مورد در یک خط)</label>
              <textarea value={formData.cons} onChange={e => setFormData({...formData, cons: e.target.value})} placeholder="وزن زیاد&#10;قیمت بالا" />
            </InputGroup>
          </ScoreGrid>

          <ScoreGrid>
            <InputGroup>
              <label>امتیاز کلی (۱ تا ۵)</label>
              <input type="number" min="1" max="5" required value={formData.overall} onChange={e => setFormData({...formData, overall: e.target.value})} />
            </InputGroup>
            <InputGroup>
              <label>ارزش در برابر قیمت (۱ تا ۵)</label>
              <input type="number" min="1" max="5" required value={formData.value_for_money} onChange={e => setFormData({...formData, value_for_money: e.target.value})} />
            </InputGroup>
            <InputGroup>
              <label>کیفیت ساخت (۱ تا ۵)</label>
              <input type="number" min="1" max="5" required value={formData.quality} onChange={e => setFormData({...formData, quality: e.target.value})} />
            </InputGroup>
            <InputGroup>
              <label>عملکرد (۱ تا ۵)</label>
              <input type="number" min="1" max="5" required value={formData.performance} onChange={e => setFormData({...formData, performance: e.target.value})} />
            </InputGroup>
          </ScoreGrid>

          <SubmitBtn type="submit" disabled={submitting}>
            {submitting ? 'در حال ثبت...' : 'ثبت نهایی نظر'}
          </SubmitBtn>
        </FormContainer>
      )}

      {/* لیست نظرات */}
      <div>
        {loading ? (
          <p style={{ textAlign: 'center', color: 'var(--textMuted)' }}>در حال دریافت نظرات...</p>
        ) : reviews.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--textMuted)', padding: '2rem 0' }}>هنوز نظری برای این کالا ثبت نشده است. اولین نفر باشید!</p>
        ) : (
          reviews.map(review => (
            <ReviewCard key={review.id}>
              <ReviewHeader>
                <span className="user">{review.user_name || 'کاربر سایت'} {review.is_verified_purchase && <span style={{ color: 'var(--success)', fontSize: '0.8rem' }}>(خریدار محصول)</span>}</span>
                <span className="date">{new Date(review.created_at).toLocaleDateString('fa-IR')}</span>
              </ReviewHeader>
              <ReviewTitle>{review.title}</ReviewTitle>
              <ReviewBody>{review.body}</ReviewBody>

              {(review.pros || review.cons) && (
                <ProsCons>
                  {review.pros && (
                    <div className="list">
                      {review.pros.split('\n').filter(p => p.trim() !== '').map((pro, i) => (
                        <div key={i} className="pro-item">➕ {pro}</div>
                      ))}
                    </div>
                  )}
                  {review.cons && (
                    <div className="list">
                      {review.cons.split('\n').filter(c => c.trim() !== '').map((con, i) => (
                        <div key={i} className="con-item">➖ {con}</div>
                      ))}
                    </div>
                  )}
                </ProsCons>
              )}
            </ReviewCard>
          ))
        )}
      </div>
    </Container>
  );
}