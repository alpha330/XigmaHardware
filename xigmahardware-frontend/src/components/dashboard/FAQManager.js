'use client';

import { useState } from 'react';
import styled from '@emotion/styled';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Icon } from '@/components/ui/Icon';
import { useToast } from '@/components/ui/Toast';
import { createFAQ, updateFAQ, deleteFAQ } from '@/lib/api';
import { faPlus, faTrash, faEdit, faTimes, faCheck } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
`;

const List = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FAQItem = styled.div`
  padding: 12px 16px;
  background: ${p => p.$active ? p.theme.colors.brand[50] : p.theme.colors.surface.card};
  border: 1px solid ${p => p.$active ? p.theme.colors.brand[300] : p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.md};
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  justify-content: space-between;
  align-items: center;

  &:hover { border-color: ${p => p.theme.colors.brand[300]}; }
`;

const Form = styled.div`
  padding: 24px;
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
`;

export const FAQManager = ({ initialFAQs, categories }) => {
  const [faqs, setFaqs] = useState(initialFAQs);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ question: '', answer: '', category: '', is_active: true });
  const [isNew, setIsNew] = useState(false);
  const toast = useToast();

  const handleSelect = (faq) => {
    setSelected(faq);
    setIsNew(false);
    setForm({ question: faq.question, answer: faq.answer, category: faq.category || '', is_active: faq.is_active });
  };

  const handleNew = () => {
    setSelected(null);
    setIsNew(true);
    setForm({ question: '', answer: '', category: categories[0]?.id || '', is_active: true });
  };

  const handleSave = async () => {
    if (!form.question || !form.answer) {
      toast.warning('سوال و جواب الزامی است');
      return;
    }

    if (isNew) {
      const res = await createFAQ(form);
      if (res.success) {
        toast.success('سوال اضافه شد');
        setFaqs([...faqs, res.data]);
        handleNew();
      } else {
        toast.error(res.error);
      }
    } else if (selected) {
      const res = await updateFAQ(selected.id, form);
      if (res.success) {
        toast.success('بروزرسانی شد');
        setFaqs(faqs.map(f => f.id === selected.id ? { ...f, ...form } : f));
        setSelected({ ...selected, ...form });
      } else {
        toast.error(res.error);
      }
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('آیا مطمئن هستید؟')) return;
    const res = await deleteFAQ(id);
    if (res.success) {
      toast.success('حذف شد');
      setFaqs(faqs.filter(f => f.id !== id));
      if (selected?.id === id) { setSelected(null); setIsNew(false); }
    } else {
      toast.error(res.error);
    }
  };

  return (
    <Grid>
      <div>
        <Button variant="primary" size="sm" icon={faPlus} onClick={handleNew} style={{ marginBottom: 16 }}>
          سوال جدید
        </Button>
        <List>
          {faqs.map(faq => (
            <FAQItem key={faq.id} $active={selected?.id === faq.id} onClick={() => handleSelect(faq)}>
              <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {faq.question}
              </span>
              <Button variant="ghost" size="sm" icon={faTrash} onClick={(e) => { e.stopPropagation(); handleDelete(faq.id); }} />
            </FAQItem>
          ))}
        </List>
      </div>

      {(isNew || selected) && (
        <Form>
          <h3 style={{ marginBottom: 20 }}>{isNew ? 'سوال جدید' : 'ویرایش سوال'}</h3>
          <Input label="سوال" value={form.question} onChange={(e) => setForm({ ...form, question: e.target.value })} />
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: '0.9rem' }}>دسته‌بندی</label>
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid #e2e8f0',
                fontFamily: 'inherit', fontSize: '0.9rem', background: 'white',
              }}
            >
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 6, fontWeight: 500, fontSize: '0.9rem' }}>جواب</label>
            <textarea
              value={form.answer}
              onChange={(e) => setForm({ ...form, answer: e.target.value })}
              rows={5}
              style={{
                width: '100%', padding: '10px 12px', borderRadius: 8, border: '1px solid #e2e8f0',
                fontFamily: 'inherit', fontSize: '0.9rem', resize: 'vertical',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button variant="primary" icon={faCheck} onClick={handleSave}>ذخیره</Button>
            <Button variant="ghost" icon={faTimes} onClick={() => { setSelected(null); setIsNew(false); }}>انصراف</Button>
          </div>
        </Form>
      )}
    </Grid>
  );
};