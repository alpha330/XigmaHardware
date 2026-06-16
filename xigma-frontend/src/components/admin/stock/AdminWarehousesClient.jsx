// src/components/admin/stock/AdminWarehousesClient.jsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import styled from '@emotion/styled';
import { apiFetch } from '../../../utils/apiFetch';
import { useToast } from '../../ui/ToastProvider';
import { GoogleMap, useLoadScript, Marker } from '@react-google-maps/api';

// ================= STYLES =================
const PageWrapper = styled.div`
  padding: 2rem;
  background-color: ${({ theme }) => theme.colors.background};
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};
`;

const Title = styled.h1`
  font-size: 1.8rem;
  color: ${({ theme }) => theme.colors.textMain};
`;

const CreateBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary};
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
  &:hover { opacity: 0.9; }
`;

// --- Grid & Cards ---
const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
`;

const WarehouseCard = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    transform: translateY(-3px);
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.05);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  h3 { margin: 0; color: ${({ theme }) => theme.colors.textMain}; font-size: 1.2rem; }
  .code { font-family: monospace; color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.85rem; }
`;

const Badge = styled.span`
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: bold;
  background-color: ${({ theme, active }) => active ? `${theme.colors.success}15` : `${theme.colors.error}15`};
  color: ${({ theme, active }) => active ? theme.colors.success : theme.colors.error};
`;

const ProgressBar = styled.div`
  width: 100%; height: 8px; background-color: ${({ theme }) => theme.colors.background};
  border-radius: 4px; overflow: hidden; margin-top: 0.5rem;

  .fill {
    height: 100%;
    background-color: ${({ percent, theme }) => percent > 90 ? theme.colors.error : percent > 70 ? theme.colors.warning : theme.colors.primary};
    width: ${({ percent }) => Math.min(percent, 100)}%;
  }
`;

const InfoRow = styled.div`
  display: flex; justify-content: space-between; font-size: 0.85rem; color: ${({ theme }) => theme.colors.textMuted};
`;

// --- Modal Styles ---
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.6); display: flex; align-items: center; justify-content: center;
  z-index: 9999; padding: 1rem;
`;

const ModalContent = styled.div`
  background-color: ${({ theme }) => theme.colors.surface};
  border-radius: 16px; width: 100%; max-width: 800px; padding: 2rem;
  max-height: 90vh; overflow-y: auto;

  &::-webkit-scrollbar { width: 6px; }
  &::-webkit-scrollbar-thumb { background-color: ${({ theme }) => theme.colors.border}; border-radius: 4px; }
`;

const SectionTitle = styled.h3`
  font-size: 1.1rem; color: ${({ theme }) => theme.colors.primary};
  margin: 1.5rem 0 1rem 0; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; padding-bottom: 0.5rem;
`;

const FormGrid = styled.div`
  display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
  @media (max-width: 600px) { grid-template-columns: 1fr; }
`;

const FormGroup = styled.div`
  display: flex; flex-direction: column; gap: 0.5rem;
  &.full-width { grid-column: 1 / -1; }

  label { font-weight: bold; font-size: 0.9rem; color: ${({ theme }) => theme.colors.textMain}; }
  input, select, textarea {
    padding: 0.8rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
    background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain};
    font-family: inherit; outline: none;
    &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
  }
  textarea { resize: vertical; min-height: 80px; }
  select[multiple] { min-height: 100px; }
`;

const ModalActions = styled.div`
  display: flex; gap: 1rem; margin-top: 2rem; position: sticky; bottom: -2rem;
  background: ${({ theme }) => theme.colors.surface}; padding: 1rem 0; border-top: 1px solid ${({ theme }) => theme.colors.border};

  button {
    flex: 1; padding: 1rem; border-radius: 8px; font-weight: bold; cursor: pointer; border: none;
    &.cancel { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain}; border: 1px solid ${({ theme }) => theme.colors.border}; }
    &.submit { background-color: ${({ theme }) => theme.colors.primary}; color: #fff; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
`;

const defaultFormState = {
  code: '', name: '', warehouse_type: 'main', scope: 'general', description: '',
  parent: '', manager: '', staff: [], phone: '', email: '',
  capacity: 0, is_active: true, is_public: false,
  address: '', specialization: '',
  latitude: '', longitude: '' // 🎯 مقادیر نقشه
};

export default function AdminWarehousesClient() {
  const { showToast } = useToast();
  const [warehouses, setWarehouses] = useState([]);
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(true);

  // 🎯 بارگذاری اسکریپت نقشه گوگل
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "",
    // نکته: اگر API Key ندارید، نقشه در حالت For Development Purposes Only لود می‌شود ولی کار می‌کند.
  });

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState(defaultFormState);

  const fetchWarehouses = async () => {
    setLoading(true);
    try {
      const res = await apiFetch('/api/v1/stock/warehouses/', { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setWarehouses(data.results || data);
      }
    } catch (error) {
      showToast('خطا در دریافت لیست انبارها', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await apiFetch('/api/v1/accounts/users/');
      if (res.ok) {
        const data = await res.json();
        setUsersList(data.results || data);
      }
    } catch (error) {
      console.error("Failed to fetch users list");
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchWarehouses();
    fetchUsers();
  }, []);

  const handleOpenCreateModal = () => {
    setEditId(null);
    setFormData(defaultFormState);
    setShowModal(true);
  };

  const handleOpenEditModal = async (warehouse) => {
    setEditId(warehouse.id);
    setShowModal(true);

    try {
      // 🎯 گرفتن دیتای کامل از اندپوینت Detail
      const res = await apiFetch(`/api/v1/stock/warehouses/${warehouse.id}/`, { cache: 'no-store' });
      if (res.ok) {
        const fullData = await res.json();

        setFormData({
          code: fullData.code || '',
          name: fullData.name || '',
          warehouse_type: fullData.warehouse_type || 'main',
          scope: fullData.scope || 'general',
          description: fullData.description || '',
          parent: fullData.parent || '',
          manager: fullData.manager || '',
          staff: Array.isArray(fullData.staff) ? fullData.staff : [],
          phone: fullData.phone || '',
          email: fullData.email || '',
          capacity: fullData.capacity || 0,
          is_active: fullData.is_active !== false,
          is_public: fullData.is_public || false,
          address: fullData.address || '',
          specialization: fullData.specialization || '',
          latitude: fullData.latitude || '',
          longitude: fullData.longitude || ''
        });
      }
    } catch (error) {
      showToast('خطا در دریافت جزئیات انبار', 'error');
    }
  };

  const handleMultiSelectChange = (e) => {
    const value = Array.from(e.target.selectedOptions, option => option.value);
    setFormData({ ...formData, staff: value });
  };

  // 🎯 هندلر کلیک روی نقشه
  const onMapClick = useCallback((e) => {
    setFormData(prev => ({
      ...prev,
      latitude: e.latLng.lat().toFixed(6),
      longitude: e.latLng.lng().toFixed(6)
    }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = { ...formData };
    if (!payload.parent) payload.parent = null;
    if (!payload.manager) payload.manager = null;
    if (!payload.latitude) payload.latitude = null;
    if (!payload.longitude) payload.longitude = null;

    try {
      const method = editId ? 'PATCH' : 'POST';
      const endpoint = editId ? `/api/v1/stock/warehouses/${editId}/` : '/api/v1/stock/warehouses/';

      const res = await apiFetch(endpoint, {
        method,
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) {
        const errorMsg = typeof data === 'object'
          ? Object.entries(data).map(([key, val]) => `${key}: ${val}`).join(' | ')
          : 'خطا در ذخیره‌سازی اطلاعات';
        throw new Error(errorMsg);
      }

      showToast(editId ? 'انبار با موفقیت بروزرسانی شد.' : 'انبار با موفقیت ایجاد شد.', 'success');
      setShowModal(false);
      fetchWarehouses(); // رفرش لیست
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <PageWrapper>
      <Header>
        <Title>🏢 مدیریت پیشرفته انبارها</Title>
        <CreateBtn onClick={handleOpenCreateModal}>➕ تعریف انبار جدید</CreateBtn>
      </Header>

      {loading ? (
        <p style={{ textAlign: 'center', color: 'var(--textMuted)', padding: '3rem' }}>در حال بارگذاری...</p>
      ) : warehouses.length === 0 ? (
        <p style={{ textAlign: 'center', color: 'var(--textMuted)', padding: '3rem' }}>هیچ انباری یافت نشد.</p>
      ) : (
        <Grid>
          {warehouses.map(wh => {
            const utilization = wh.capacity > 0 ? (wh.current_items / wh.capacity) * 100 : 0;
            return (
              <WarehouseCard key={wh.id} onClick={() => handleOpenEditModal(wh)}>
                <CardHeader>
                  <div>
                    <h3>{wh.name}</h3>
                    <span className="code">{wh.code}</span>
                  </div>
                  <Badge active={wh.is_active}>{wh.is_active ? 'فعال' : 'غیرفعال'}</Badge>
                </CardHeader>

                <div style={{ marginTop: '0.5rem' }}>
                  <InfoRow style={{ marginBottom: '0.3rem' }}>
                    <span>تراکم موجودی:</span>
                    <span style={{ fontWeight: 'bold', color: 'var(--textMain)' }}>
                      {wh.current_items} از {wh.capacity}
                    </span>
                  </InfoRow>
                  <ProgressBar percent={utilization}>
                    <div className="fill" />
                  </ProgressBar>
                </div>

                <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1rem', marginTop: '0.5rem' }}>
                  <InfoRow><span>مدیر انبار:</span><span>{wh.manager_name || 'تعیین نشده'}</span></InfoRow>
                  <InfoRow><span>دسترسی:</span><span>{wh.is_public ? 'عمومی' : 'اختصاصی'}</span></InfoRow>
                  <InfoRow><span>نوع انبار:</span><span>{wh.warehouse_type || 'Main'}</span></InfoRow>
                </div>
              </WarehouseCard>
            );
          })}
        </Grid>
      )}

      {/* Modal ایجاد / ویرایش انبار */}
      {showModal && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setShowModal(false); }}>
          <ModalContent>
            <h2 style={{ color: 'var(--textMain)' }}>{editId ? 'ویرایش انبار' : 'تعریف انبار جدید'}</h2>

            <form onSubmit={handleSubmit}>

              <SectionTitle>اطلاعات پایه (Basic Information)</SectionTitle>
              <FormGrid>
                <FormGroup>
                  <label>کد انبار (Warehouse Code)</label>
                  <input required value={formData.code} onChange={e => setFormData({...formData, code: e.target.value})} placeholder="مثال: WH-MAIN-001" dir="ltr" />
                </FormGroup>
                <FormGroup>
                  <label>نام انبار (Warehouse Name)</label>
                  <input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="مثال: انبار مرکزی تهران" />
                </FormGroup>
                <FormGroup>
                  <label>نوع (Type)</label>
                  <select value={formData.warehouse_type} onChange={e => setFormData({...formData, warehouse_type: e.target.value})}>
                    <option value="main">انبار اصلی (Main Warehouse)</option>
                    <option value="sub">انبار فرعی (Sub Warehouse)</option>
                    <option value="transit">انبار ترانزیت</option>
                  </select>
                </FormGroup>
                <FormGroup>
                  <label>حوزه فعالیت (Scope)</label>
                  <select value={formData.scope} onChange={e => setFormData({...formData, scope: e.target.value})}>
                    <option value="general">عمومی (General Hardware)</option>
                    <option value="specialized">تخصصی (Specialized)</option>
                  </select>
                </FormGroup>
                <FormGroup className="full-width">
                  <label>توضیحات (Description)</label>
                  <textarea value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
                </FormGroup>
              </FormGrid>

              <SectionTitle>سلسله مراتب (Hierarchy)</SectionTitle>
              <FormGrid>
                <FormGroup className="full-width">
                  <label>انبار بالادستی (Parent Warehouse)</label>
                  <select value={formData.parent} onChange={e => setFormData({...formData, parent: e.target.value})}>
                    <option value="">بدون والد (انبار اصلی)</option>
                    {warehouses.filter(w => w.id !== editId).map(w => (
                      <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
                    ))}
                  </select>
                </FormGroup>
                <FormGroup>
                  <label>مدیر انبار (Warehouse Manager)</label>
                  <select value={formData.manager} onChange={e => setFormData({...formData, manager: e.target.value})}>
                    <option value="">انتخاب نشده</option>
                    {usersList.map(u => {
                      const displayName = (u.first_name || u.last_name)
                        ? `${u.first_name || ''} ${u.last_name || ''}`.trim()
                        : (u.email || u.mobile || 'کاربر بدون نام');
                      return <option key={u.id} value={u.id}>{displayName}</option>;
                    })}
                  </select>
                </FormGroup>
                <FormGroup>
                  <label>پرسنل انبار (Staff) - با نگه داشتن Ctrl انتخاب کنید</label>
                  <select multiple value={formData.staff} onChange={handleMultiSelectChange}>
                    {usersList.map(u => {
                      const displayName = (u.first_name || u.last_name)
                        ? `${u.first_name || ''} ${u.last_name || ''}`.trim()
                        : (u.email || u.mobile || 'کاربر بدون نام');
                      return <option key={u.id} value={u.id}>{displayName}</option>;
                    })}
                  </select>
                </FormGroup>
              </FormGrid>

              <SectionTitle>اطلاعات تماس و مکان (Contact & Location)</SectionTitle>
              <FormGrid>
                <FormGroup>
                  <label>تلفن (Phone)</label>
                  <input value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} dir="ltr" />
                </FormGroup>
                <FormGroup>
                  <label>ایمیل (Email)</label>
                  <input type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} dir="ltr" />
                </FormGroup>
                <FormGroup className="full-width">
                  <label>آدرس متنی (Address)</label>
                  <textarea value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} />
                </FormGroup>

                {/* 🎯 افزوده شدن نقشه گوگل */}
                <FormGroup className="full-width">
                  <label>موقعیت روی نقشه (برای ثبت کلیک کنید)</label>
                  {isLoaded ? (
                    <div style={{ height: '300px', width: '100%', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border)' }}>
                      <GoogleMap
                        mapContainerStyle={{ width: '100%', height: '100%' }}
                        center={
                          formData.latitude && formData.longitude
                            ? { lat: parseFloat(formData.latitude), lng: parseFloat(formData.longitude) }
                            : { lat: 35.6892, lng: 51.3890 } // پیش‌فرض: تهران
                        }
                        zoom={11}
                        onClick={onMapClick}
                      >
                        {formData.latitude && formData.longitude && (
                          <Marker position={{ lat: parseFloat(formData.latitude), lng: parseFloat(formData.longitude) }} />
                        )}
                      </GoogleMap>
                    </div>
                  ) : (
                    <div style={{ padding: '2rem', textAlign: 'center', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px' }}>
                      در حال بارگذاری نقشه...
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                    <input type="text" readOnly placeholder="Latitude" value={formData.latitude} style={{ background: 'var(--surface)' }} />
                    <input type="text" readOnly placeholder="Longitude" value={formData.longitude} style={{ background: 'var(--surface)' }} />
                  </div>
                </FormGroup>
              </FormGrid>

              <SectionTitle>ظرفیت و وضعیت (Capacity & Status)</SectionTitle>
              <FormGrid>
                <FormGroup>
                  <label>ظرفیت کل (Maximum Items)</label>
                  <input type="number" required min="0" value={formData.capacity} onChange={e => setFormData({...formData, capacity: parseInt(e.target.value)})} />
                </FormGroup>
                <FormGroup>
                  <label>تخصص انبار (Specialization)</label>
                  <input value={formData.specialization} onChange={e => setFormData({...formData, specialization: e.target.value})} placeholder="مثال: فقط قطعات سرور" />
                </FormGroup>
                <div style={{ display: 'flex', gap: '2rem', gridColumn: '1 / -1', marginTop: '0.5rem' }}>
                  <FormGroup style={{ flexDirection: 'row', alignItems: 'center', gap: '0.8rem' }}>
                    <input type="checkbox" checked={formData.is_active} onChange={e => setFormData({...formData, is_active: e.target.checked})} style={{ width: '20px', height: '20px' }} />
                    <label style={{ margin: 0 }}>وضعیت فعال (Is Active)</label>
                  </FormGroup>
                  <FormGroup style={{ flexDirection: 'row', alignItems: 'center', gap: '0.8rem' }}>
                    <input type="checkbox" checked={formData.is_public} onChange={e => setFormData({...formData, is_public: e.target.checked})} style={{ width: '20px', height: '20px' }} />
                    <label style={{ margin: 0 }}>قابل مشاهده برای مشتری (Public)</label>
                  </FormGroup>
                </div>
              </FormGrid>

              <ModalActions>
                <button type="button" className="cancel" onClick={() => setShowModal(false)}>انصراف</button>
                <button type="submit" className="submit" disabled={submitting}>
                  {submitting ? 'در حال ثبت...' : (editId ? 'بروزرسانی انبار' : 'ذخیره انبار')}
                </button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}
    </PageWrapper>
  );
}