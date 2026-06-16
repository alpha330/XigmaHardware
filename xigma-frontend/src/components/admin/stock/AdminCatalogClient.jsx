// src/components/admin/stock/AdminCatalogClient.jsx
'use client';

import React, { useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../../utils/apiFetch';
import { useToast } from '../../ui/ToastProvider';
import { useRouter } from 'next/navigation';

// ================= STYLES =================
const PageWrapper = styled.div`
  padding: 2rem;
  background-color: ${({ theme }) => theme.colors.background};
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;
  padding-bottom: 1rem; border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const Title = styled.h1`
  font-size: 1.8rem; color: ${({ theme }) => theme.colors.textMain};
`;

const TabContainer = styled.div`
  display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; padding-bottom: 1rem;
`;

const TabBtn = styled.button`
  background: none; border: none; padding: 0.5rem 1rem; font-size: 1.1rem; font-weight: bold; cursor: pointer;
  color: ${({ theme, active }) => active ? theme.colors.primary : theme.colors.textMuted};
  border-bottom: 3px solid ${({ theme, active }) => active ? theme.colors.primary : 'transparent'};
  transition: all 0.2s;
  &:hover { color: ${({ theme }) => theme.colors.primary}; }
`;

const CreateBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary}; color: #fff; border: none; padding: 0.8rem 1.5rem;
  border-radius: 8px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; &:hover { opacity: 0.9; }
`;

// --- Table Styles ---
const TableContainer = styled.div`
  background-color: ${({ theme }) => theme.colors.surface}; border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px; overflow-x: auto;
`;

const Table = styled.table`
  width: 100%; border-collapse: collapse; min-width: 800px;
  th, td { padding: 1rem; text-align: right; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; }
  th { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMuted}; font-weight: bold; }
  td { color: ${({ theme }) => theme.colors.textMain}; }
`;

const Badge = styled.span`
  padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: bold;
  background-color: ${({ theme, bg }) => bg || theme.colors.border}; color: #fff;
`;

const ActionBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.secondary}; color: #fff; border: none; padding: 0.4rem 0.8rem;
  border-radius: 6px; cursor: pointer; font-size: 0.85rem;
  &:hover { opacity: 0.8; }
`;

// --- Modal Styles (مشابه صفحات قبل) ---
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 1rem;
`;

const ModalContent = styled.div`
  background-color: ${({ theme }) => theme.colors.surface}; border-radius: 16px; width: 100%; max-width: 600px; padding: 2rem;
`;

const FormGroup = styled.div`
  display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem;
  label { font-weight: bold; font-size: 0.9rem; color: ${({ theme }) => theme.colors.textMain}; }
  input, select, textarea {
    padding: 0.8rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
    background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain};
    font-family: inherit; outline: none;
  }
`;

const ModalActions = styled.div`
  display: flex; gap: 1rem; margin-top: 2rem;
  button {
    flex: 1; padding: 1rem; border-radius: 8px; font-weight: bold; cursor: pointer; border: none;
    &.cancel { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain}; border: 1px solid ${({ theme }) => theme.colors.border}; }
    &.submit { background-color: ${({ theme }) => theme.colors.primary}; color: #fff; }
  }
`;

const defaultCatForm = { name: '', slug: '', category_type: 'type', condition: '', parent: '', description: '', is_active: true };

export default function AdminCatalogClient() {
  const { showToast } = useToast();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('categories'); // 'categories', 'brands'

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  // Category Modal State
  const [showCatModal, setShowCatModal] = useState(false);
  const [editCatId, setEditCatId] = useState(null);
  const [catForm, setCatForm] = useState(defaultCatForm);
  const [submitting, setSubmitting] = useState(false);

  // Security Check
  useEffect(() => {
    const checkAccess = async () => {
      try {
        const res = await apiFetch('/api/v1/accounts/users/me/');
        if (res.ok) {
          const data = await res.json();
          const user = data.user || data;
          if (user.is_superuser || user.role === 'stock_keeper') {
            // eslint-disable-next-line react-hooks/immutability
            fetchCategories();
          } else {
            router.push('/');
          }
        }
      } catch (err) { router.push('/auth/login'); }
    };
    checkAccess();
  }, [router]);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/v1/stock/categories/', { cache: 'no-store' });
      if (res.ok) setCategories((await res.json()).results || await res.json());
    } catch (err) { showToast('خطا در دریافت دسته‌بندی‌ها', 'error'); }
    finally { setLoading(false); }
  };

  const handleOpenCatModal = (cat = null) => {
    if (cat) {
      setEditCatId(cat.id);
      setCatForm({
        name: cat.name || '', slug: cat.slug || '',
        category_type: cat.category_type || 'type',
        condition: cat.condition || '',
        parent: cat.parent || '',
        description: cat.description || '',
        is_active: cat.is_active !== false
      });
    } else {
      setEditCatId(null);
      setCatForm(defaultCatForm);
    }
    setShowCatModal(true);
  };

  const handleCatSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = { ...catForm };
    if (!payload.parent) payload.parent = null;
    if (!payload.condition) payload.condition = null;

    try {
      const method = editCatId ? 'PATCH' : 'POST';
      const endpoint = editCatId ? `/api/v1/stock/categories/${editCatId}/` : '/api/v1/stock/categories/';
      const res = await apiFetch(endpoint, { method, body: JSON.stringify(payload) });

      if (!res.ok) throw new Error('خطا در ذخیره دسته‌بندی');

      showToast('عملیات با موفقیت انجام شد', 'success');
      setShowCatModal(false);
      fetchCategories();
    } catch (err) { showToast(err.message, 'error'); }
    finally { setSubmitting(false); }
  };

  // Helper function to colorize category badges based on your python dict
  const getCatTypeColor = (type) => {
    const colors = { 'condition': '#28a745', 'usage': '#17a2b8', 'brand': '#ffc107', 'type': '#6f42c1', 'series': '#dc3545' };
    return colors[type] || '#6c757d';
  };

  return (
    <PageWrapper>
      <Header>
        <Title>🗂️ مدیریت ساختار و کاتالوگ</Title>
        {activeTab === 'categories' && <CreateBtn onClick={() => handleOpenCatModal()}>➕ دسته‌بندی جدید</CreateBtn>}
        {/* Later: Add Button for Brands */}
      </Header>

      <TabContainer>
        <TabBtn active={activeTab === 'categories'} onClick={() => setActiveTab('categories')}>دسته‌بندی‌ها</TabBtn>
        <TabBtn active={activeTab === 'brands'} onClick={() => setActiveTab('brands')}>برندها و سری‌ها (بزودی)</TabBtn>
      </TabContainer>

      {activeTab === 'categories' && (
        <TableContainer>
          <Table>
            <thead>
              <tr>
                <th>نام دسته‌بندی</th>
                <th>نوع (Type)</th>
                <th>سلسله مراتب</th>
                <th>وضعیت</th>
                <th>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {loading ? <tr><td colSpan="5" style={{textAlign:'center'}}>در حال بارگذاری...</td></tr> :
                categories.map(cat => (
                  <tr key={cat.id}>
                    <td style={{fontWeight:'bold'}}>{cat.name}</td>
                    <td><Badge bg={getCatTypeColor(cat.category_type)}>{cat.category_type}</Badge></td>
                    <td>{cat.parent ? 'دارای والد' : 'ریشه (Root)'} - سطح {cat.level}</td>
                    <td>{cat.is_active ? '✅ فعال' : '❌ غیرفعال'}</td>
                    <td><ActionBtn onClick={() => handleOpenCatModal(cat)}>ویرایش</ActionBtn></td>
                  </tr>
                ))
              }
            </tbody>
          </Table>
        </TableContainer>
      )}

      {/* Category Modal */}
      {showCatModal && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setShowCatModal(false); }}>
          <ModalContent>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>{editCatId ? 'ویرایش دسته‌بندی' : 'ایجاد دسته‌بندی جدید'}</h2>
            <form onSubmit={handleCatSubmit}>
              <FormGroup>
                <label>نام دسته‌بندی</label>
                <input required value={catForm.name} onChange={e => setCatForm({...catForm, name: e.target.value})} placeholder="مثال: سرورهای رکمونت" />
              </FormGroup>

              <FormGroup>
                <label>Slug (شناسه URL)</label>
                <input required value={catForm.slug} onChange={e => setCatForm({...catForm, slug: e.target.value})} dir="ltr" />
              </FormGroup>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <FormGroup>
                  <label>نوع دسته‌بندی</label>
                  <select value={catForm.category_type} onChange={e => setCatForm({...catForm, category_type: e.target.value})}>
                    <option value="type">نوع محصول (Type)</option>
                    <option value="brand">برند (Brand)</option>
                    <option value="usage">کاربری (Usage)</option>
                    <option value="condition">وضعیت فیزیکی (Condition)</option>
                    <option value="series">سری (Series)</option>
                  </select>
                </FormGroup>

                <FormGroup>
                  <label>دسته‌بندی والد</label>
                  <select value={catForm.parent} onChange={e => setCatForm({...catForm, parent: e.target.value})}>
                    <option value="">(بدون والد - دسته اصلی)</option>
                    {categories.filter(c => c.id !== editCatId).map(c => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </FormGroup>
              </div>

              <FormGroup style={{ flexDirection: 'row', alignItems: 'center', marginTop: '1rem' }}>
                <input type="checkbox" checked={catForm.is_active} onChange={e => setCatForm({...catForm, is_active: e.target.checked})} style={{ width: 'auto' }} />
                <label style={{ margin: 0 }}>وضعیت فعال</label>
              </FormGroup>

              <ModalActions>
                <button type="button" className="cancel" onClick={() => setShowCatModal(false)}>انصراف</button>
                <button type="submit" className="submit" disabled={submitting}>{submitting ? 'در حال ثبت...' : 'ذخیره'}</button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}

    </PageWrapper>
  );
}