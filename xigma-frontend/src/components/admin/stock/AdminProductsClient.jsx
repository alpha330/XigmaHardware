// src/components/admin/stock/AdminProductsClient.jsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
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
  padding-bottom: 1rem; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; flex-wrap: wrap; gap: 1rem;
`;

const Title = styled.h1`
  font-size: 1.8rem; color: ${({ theme }) => theme.colors.textMain}; display: flex; align-items: center; gap: 0.8rem;
`;

const ControlsContainer = styled.div`
  display: flex; gap: 1rem; align-items: center;
`;

const SearchInput = styled.input`
  padding: 0.8rem 1.2rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
  background-color: ${({ theme }) => theme.colors.surface}; color: ${({ theme }) => theme.colors.textMain};
  width: 250px; font-family: inherit; outline: none; &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
`;

const CreateBtn = styled.button`
  background-color: ${({ theme }) => theme.colors.primary}; color: #fff; border: none; padding: 0.8rem 1.5rem;
  border-radius: 8px; font-weight: bold; cursor: pointer; transition: opacity 0.2s; &:hover { opacity: 0.9; }
`;

// --- Table Styles ---
const TableContainer = styled.div`
  background-color: ${({ theme }) => theme.colors.surface}; border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: 12px; overflow-x: auto; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
`;

const Table = styled.table`
  width: 100%; border-collapse: collapse; min-width: 1100px;
  th, td { padding: 1rem; text-align: right; border-bottom: 1px solid ${({ theme }) => theme.colors.border}; }
  th { background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMuted}; font-size: 0.9rem; font-weight: bold; }
  td { color: ${({ theme }) => theme.colors.textMain}; font-size: 0.95rem; vertical-align: middle; }
  tbody tr:hover { background-color: ${({ theme }) => theme.colors.background}; }
`;

const StatusBadge = styled.span`
  padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: bold;
  background-color: ${({ theme, status }) => status === 'published' ? `${theme.colors.success}15` : `${theme.colors.warning}15`};
  color: ${({ theme, status }) => status === 'published' ? theme.colors.success : theme.colors.warning};
`;

const ActionBtn = styled.button`
  background-color: ${({ theme, variant }) => variant === 'danger' ? theme.colors.error : variant === 'info' ? theme.colors.secondary : variant === 'dark' ? theme.colors.border : theme.colors.primary};
  color: ${({ variant, theme }) => variant === 'dark' ? theme.colors.textMain : '#fff'};
  border: none; padding: 0.5rem 0.8rem; border-radius: 6px; font-size: 0.85rem; font-weight: bold; cursor: pointer; transition: opacity 0.2s; margin-left: 0.5rem;
  &:hover:not(:disabled) { opacity: 0.8; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

// --- Modal Styles ---
const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.6);
  display: flex; align-items: center; justify-content: center; z-index: 9999; padding: 1rem;
`;

const ModalContent = styled.div`
  background-color: ${({ theme }) => theme.colors.surface}; border-radius: 16px; width: 100%;
  max-width: 800px; padding: 2rem; max-height: 90vh; overflow-y: auto;
  &::-webkit-scrollbar { width: 6px; }
  &::-webkit-scrollbar-thumb { background-color: ${({ theme }) => theme.colors.border}; border-radius: 4px; }
`;

const FormGrid = styled.div`
  display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;
  @media (max-width: 600px) { grid-template-columns: 1fr; }
`;

const FormGroup = styled.div`
  display: flex; flex-direction: column; gap: 0.5rem;
  &.full-width { grid-column: 1 / -1; }
  label { font-weight: bold; font-size: 0.9rem; color: ${({ theme }) => theme.colors.textMain}; }
  input, select, textarea {
    padding: 0.8rem; border-radius: 8px; border: 1px solid ${({ theme }) => theme.colors.border};
    background-color: ${({ theme }) => theme.colors.background}; color: ${({ theme }) => theme.colors.textMain};
    font-family: inherit; outline: none; &:focus { border-color: ${({ theme }) => theme.colors.primary}; }
  }
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

// --- Image Upload Specific Styles ---
const ImageGallery = styled.div`
  display: flex; gap: 1rem; overflow-x: auto; padding-bottom: 1rem; margin-bottom: 1.5rem;
  img { width: 100px; height: 100px; object-fit: cover; border-radius: 8px; border: 2px solid ${({ theme }) => theme.colors.border}; }
  .main-img { border-color: ${({ theme }) => theme.colors.success}; position: relative; }
  .main-badge { position: absolute; top: -5px; right: -5px; background: ${({ theme }) => theme.colors.success}; color: #fff; font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 10px; }
  .img-wrapper { position: relative; display: inline-block; }
`;

const FileUploadBox = styled.div`
  border: 2px dashed ${({ theme }) => theme.colors.border}; border-radius: 12px; padding: 2rem; text-align: center;
  background: ${({ theme }) => theme.colors.background}; cursor: pointer; transition: all 0.2s;
  &:hover { border-color: ${({ theme }) => theme.colors.primary}; }
  input[type="file"] { display: none; }
`;

const defaultProductForm = {
  name: '', sku: '', category: '', brand: '', condition: 'new',
  model_number: '', processor: '', min_stock_alert: 5, description: '', is_active: true
};

export default function AdminProductsClient() {
  const { showToast } = useToast();
  const router = useRouter();
  const fileInputRef = useRef(null);

  const [isAuthorized, setIsAuthorized] = useState(false);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);

  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Modals State
  const [publishModalObj, setPublishModalObj] = useState(null);

  const [showProductModal, setShowProductModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [productForm, setProductForm] = useState(defaultProductForm);
  const [submitting, setSubmitting] = useState(false);

  const [publishForm, setPublishForm] = useState({
    market_quantity: '',
    market_price: '',
    market_description: '',
    market_tags: ''
  });

  // Image Modal State
  const [imageModalObj, setImageModalObj] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [isMainImage, setIsMainImage] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 1. Check Access
  useEffect(() => {
    const checkAccess = async () => {
      try {
        const res = await apiFetch('/api/v1/accounts/users/me/');
        if (res.ok) {
          const data = await res.json();
          const user = data.user || data;
          const allowedRoles = ['super_admin', 'stock_keeper'];

          if (user.is_superuser || allowedRoles.includes(user.role)) {
            setIsAuthorized(true);
            // eslint-disable-next-line react-hooks/immutability
            fetchInitialData();
          } else {
            showToast('شما دسترسی لازم برای مشاهده این پنل را ندارید.', 'error');
            router.push('/');
          }
        } else {
          router.push('/auth/login');
        }
      } catch (error) {
        router.push('/auth/login');
      }
    };
    checkAccess();
  }, [router, showToast]);

  // 2. Fetch Initial Base Data
  const fetchInitialData = async () => {
    try {
      const [catsRes, brandsRes] = await Promise.all([
        apiFetch('/api/v1/stock/categories/'),
        apiFetch('/api/v1/stock/brands/')
      ]);
      if (catsRes.ok) setCategories((await catsRes.json()).results || await catsRes.json());
      if (brandsRes.ok) setBrands((await brandsRes.json()).results || await brandsRes.json());
    } catch (error) {
      console.error('Failed to fetch base data');
    }
  };

  // 3. Fetch Products
  const fetchProducts = async (query = '') => {
    setLoading(true);
    try {
      const url = query ? `/api/v1/stock/products/?search=${query}` : '/api/v1/stock/products/';
      const res = await apiFetch(url, { cache: 'no-store' });
      if (res.ok) {
        setProducts((await res.json()).results || await res.json());
      } else {
        throw new Error('خطا در دریافت لیست محصولات');
      }
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAuthorized) return;
    const timer = setTimeout(() => { fetchProducts(search); }, 500);
    return () => clearTimeout(timer);
  }, [search, isAuthorized]);

  if (!isAuthorized) {
    return <div style={{ textAlign: 'center', padding: '5rem', fontSize: '1.2rem' }}>در حال بررسی دسترسی امنیتی... 🔒</div>;
  }

  // ================= PRODUCT HANDLERS =================
  const handleOpenCreateProduct = () => {
    setEditId(null);
    setProductForm(defaultProductForm);
    setShowProductModal(true);
  };

  const handleOpenEditProduct = async (product) => {
    setEditId(product.id);
    setShowProductModal(true);
    try {
      const res = await apiFetch(`/api/v1/stock/products/${product.id}/`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        setProductForm({
          name: data.name || '',
          sku: data.sku || '',

          // 🎯 در نسخه جدید بک‌اند، این فیلدها مستقیماً ID را برمی‌گردانند، پس نیازی به .id نداریم
          category: data.category || '',
          brand: data.brand || '',
          series: data.series || '',

          condition: data.condition || 'new',
          model_number: data.model_number || '',
          processor: data.processor || '',
          min_stock_alert: data.min_stock_alert || 5,
          description: data.description || '',
          is_active: data.is_active !== false,
        });
      }
    } catch (error) {
      showToast('خطا در دریافت اطلاعات کالا', 'error');
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const payload = { ...productForm };
    if (!payload.category) payload.category = null;
    if (!payload.brand) payload.brand = null;

    try {
      const res = await apiFetch(editId ? `/api/v1/stock/products/${editId}/` : '/api/v1/stock/products/', {
        method: editId ? 'PATCH' : 'POST',
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('خطا در ثبت کالا');

      showToast(editId ? 'کالا بروزرسانی شد.' : 'کالای جدید ثبت شد.', 'success');
      setShowProductModal(false);
      fetchProducts(search);
    } catch (error) { showToast(error.message, 'error'); }
    finally { setSubmitting(false); }
  };

  // ================= IMAGE UPLOAD HANDLERS =================
  const handleOpenImageModal = async (product) => {
    // ابتدا استیت‌های قبلی را پاک می‌کنیم و مودال را با یک آبجکت موقت باز می‌کنیم تا کاربر معطل نشود
    setImageFile(null);
    setIsMainImage(false);
    setImageModalObj({ id: product.id, name: product.name, images: [] });

    try {
      // 🎯 گرفتن اطلاعات کامل محصول از سرور برای دسترسی به آرایه images
      const res = await apiFetch(`/api/v1/stock/products/${product.id}/`, { cache: 'no-store' });
      if (res.ok) {
        const fullProductData = await res.json();
        setImageModalObj(fullProductData); // حالا آبجکت کامل (شامل عکس‌ها) را جایگزین می‌کنیم
      } else {
        throw new Error('دریافت تصاویر با خطا مواجه شد');
      }
    } catch (error) {
      showToast(error.message, 'error');
    }
  };

  const handleImageUpload = async (e) => {
    e.preventDefault();
    if (!imageFile) return showToast('لطفا یک تصویر انتخاب کنید', 'error');

    setUploading(true);
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('is_main', isMainImage ? 'True' : 'False');

    try {
      const res = await apiFetch(`/api/v1/stock/products/${imageModalObj.id}/upload_image/`, {
        method: 'POST',
        body: formData,
        // apiFetch ما به صورت خودکار Content-Type را برای FormData ست نمی‌کند که این عالی است
      });

      if (!res.ok) throw new Error('خطا در آپلود تصویر');

      showToast('تصویر با موفقیت آپلود شد', 'success');
      setImageFile(null);
      setIsMainImage(false);

      // آپدیت کردن لیست برای دیدن تغییرات در پس‌زمینه
      fetchProducts(search);

      // آپدیت کردن آبجکت مودال برای نمایش فوری عکس جدید
      const updatedProductRes = await apiFetch(`/api/v1/stock/products/${imageModalObj.id}/`, { cache: 'no-store' });
      if (updatedProductRes.ok) {
        setImageModalObj(await updatedProductRes.json());
      }

    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setUploading(false);
    }
  };

  // ================= MARKET HANDLERS =================
  const handleOpenPublishModal = (product) => {
    setPublishModalObj(product);
    setPublishForm({
      market_quantity: product.available_stock > 0 ? 1 : 0,
      market_price: product.market_price || product.selling_price || '',
      market_description: product.market_description || '',
      market_tags: product.market_tags || ''
    });
  };

  const handlePublishSubmit = async (e) => {
    e.preventDefault();
    if (publishForm.market_quantity <= 0) return showToast('تعداد نامعتبر است', 'error');
    if (publishForm.market_quantity > publishModalObj.available_stock) {
      return showToast(`حداکثر موجودی قابل انتقال ${publishModalObj.available_stock} است.`, 'error');
    }

    setSubmitting(true);
    try {
      const res = await apiFetch(`/api/v1/stock/products/${publishModalObj.id}/publish_to_market/`, {
        method: 'POST',
        body: JSON.stringify({
          market_quantity: parseInt(publishForm.market_quantity),
          // تبدیل به استرینگ (همانطور که Swagger خواسته بود) یا ارسال null
          market_price: publishForm.market_price ? String(publishForm.market_price) : null,
          market_description: publishForm.market_description,
          market_tags: publishForm.market_tags
        })
      });

      if (!res.ok) {
        const data = await res.json();
        // خواندن ارورهای اختصاصی جنگو
        const errorMsg = typeof data === 'object' ? Object.values(data).join(' | ') : 'خطا در انتقال به مارکت';
        throw new Error(errorMsg);
      }

      showToast('محصول با موفقیت در فروشگاه منتشر شد! 🚀', 'success');
      setPublishModalObj(null);
      fetchProducts(search);
    } catch (error) {
      showToast(error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRemoveFromMarket = async (product) => {
    const confirm = window.confirm(`از بازگرداندن ${product.name} به انبار مطمئن هستید؟`);
    if (!confirm) return;
    try {
      const res = await apiFetch(`/api/v1/stock/products/${product.id}/remove_from_market/`, {
        method: 'POST', body: JSON.stringify({ quantity: product.market_quantity })
      });
      if (!res.ok) throw new Error('خطا در حذف از مارکت');
      showToast('محصول به انبار بازگشت.', 'success'); fetchProducts(search);
    } catch (error) { showToast(error.message, 'error'); }
  };

  return (
    <PageWrapper>
      <Header>
        <Title>📦 مدیریت یکپارچه کالاها</Title>
        <ControlsContainer>
          <SearchInput placeholder="جستجوی نام یا SKU..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <CreateBtn onClick={handleOpenCreateProduct}>➕ تعریف کالای جدید</CreateBtn>
        </ControlsContainer>
      </Header>

      <TableContainer>
        <Table>
          <thead>
            <tr>
              <th>تصویر</th>
              <th>نام کالا</th>
              <th>SKU (کد انبار)</th>
              <th>وضعیت</th>
              <th>موجودی کل</th>
              <th>آزاد</th>
              <th>مارکت</th>
              <th>عملیات کالا</th>
              <th>عملیات مارکت</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="9" style={{ textAlign: 'center', padding: '2rem' }}>در حال بارگذاری...</td></tr>
            ) : products.length === 0 ? (
              <tr><td colSpan="9" style={{ textAlign: 'center', padding: '2rem' }}>هیچ کالایی یافت نشد.</td></tr>
            ) : (
              products.map(product => (
                <tr key={product.id}>
                  <td>
                    {product.images && product.images.length > 0 ? (
                      <img src={product.images[0].image} alt={product.name} style={{ width: '40px', height: '40px', borderRadius: '8px', objectFit: 'cover' }} />
                    ) : ( <span style={{ fontSize: '1.5rem' }}>📦</span> )}
                  </td>
                  <td style={{ fontWeight: 'bold' }}>{product.name}</td>
                  <td style={{ fontFamily: 'monospace' }}>{product.sku}</td>
                  <td>{product.condition === 'new' ? 'نو' : 'دست دوم'}</td>
                  <td>{product.total_stock} عدد</td>
                  <td style={{ color: 'var(--success)', fontWeight: 'bold' }}>{product.available_stock} عدد</td>
                  <td>
                    <StatusBadge status={product.market_status}>
                      {product.market_status === 'published' ? `${product.market_quantity} (سایت)` : 'پیش‌نویس'}
                    </StatusBadge>
                  </td>
                  <td>
                    <ActionBtn variant="dark" onClick={() => handleOpenEditProduct(product)}>ویرایش</ActionBtn>
                    <ActionBtn variant="info" onClick={() => handleOpenImageModal(product)}>🖼️ تصاویر</ActionBtn>
                  </td>
                  <td>
                    {product.market_status !== 'published' || product.market_quantity === 0 ? (
                      <ActionBtn onClick={() => handleOpenPublishModal(product)} disabled={product.available_stock <= 0}>
                        ارسال به سایت
                      </ActionBtn>
                    ) : (
                      <ActionBtn variant="danger" onClick={() => handleRemoveFromMarket(product)}>حذف از سایت</ActionBtn>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </Table>
      </TableContainer>

      {/* ================= MODALS ================= */}

      {/* Modal: Images Manager */}
      {imageModalObj && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setImageModalObj(null); }}>
          <ModalContent style={{ maxWidth: '600px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>مدیریت تصاویر: {imageModalObj.name}</h2>

            {imageModalObj.images && imageModalObj.images.length > 0 ? (
              <ImageGallery>
                {imageModalObj.images.map(img => (
                  <div key={img.id} className={`img-wrapper ${img.is_main ? 'main-img' : ''}`}>
                    {img.is_main && <span className="main-badge">اصلی</span>}
                    <img src={img.image} alt="تصویر کالا" />
                  </div>
                ))}
              </ImageGallery>
            ) : (
              <p style={{ color: 'var(--textMuted)', marginBottom: '1rem' }}>هیچ تصویری برای این کالا ثبت نشده است.</p>
            )}

            <form onSubmit={handleImageUpload} style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem' }}>
              <FileUploadBox onClick={() => fileInputRef.current?.click()}>
                <input type="file" ref={fileInputRef} accept="image/*" onChange={(e) => setImageFile(e.target.files[0])} />
                <span style={{ fontSize: '2rem' }}>📸</span>
                <p style={{ marginTop: '0.5rem', color: 'var(--textMain)' }}>
                  {imageFile ? `فایل انتخاب شد: ${imageFile.name}` : 'برای انتخاب تصویر جدید کلیک کنید'}
                </p>
              </FileUploadBox>

              {imageFile && (
                <FormGroup style={{ flexDirection: 'row', alignItems: 'center', marginTop: '1rem', justifyContent: 'center' }}>
                  <input type="checkbox" checked={isMainImage} onChange={e => setIsMainImage(e.target.checked)} style={{ width: '20px', height: '20px' }} />
                  <label style={{ margin: 0 }}>تنظیم به عنوان تصویر اصلی (کاور)</label>
                </FormGroup>
              )}

              <ModalActions>
                <button type="button" className="cancel" onClick={() => setImageModalObj(null)}>بستن</button>
                <button type="submit" className="submit" disabled={uploading || !imageFile}>
                  {uploading ? 'در حال آپلود...' : 'آپلود تصویر'}
                </button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}

      {/* Modal: Create/Edit Product Base Data */}
      {showProductModal && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setShowProductModal(false); }}>
          <ModalContent>
            <h2 style={{ color: 'var(--textMain)', marginBottom: '1.5rem' }}>{editId ? 'ویرایش کالا' : 'تعریف کالای جدید'}</h2>
            <form onSubmit={handleProductSubmit}>
              <FormGrid>
                <FormGroup><label>نام کالا</label><input required value={productForm.name} onChange={e => setProductForm({...productForm, name: e.target.value})} /></FormGroup>
                <FormGroup><label>SKU (کد انبار)</label><input required value={productForm.sku} onChange={e => setProductForm({...productForm, sku: e.target.value})} dir="ltr" /></FormGroup>
                <FormGroup><label>دسته‌بندی</label>
                  <select value={productForm.category} onChange={e => setProductForm({...productForm, category: e.target.value})}>
                    <option value="">بدون دسته بندی</option>{categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </FormGroup>
                <FormGroup><label>برند</label>
                  <select value={productForm.brand} onChange={e => setProductForm({...productForm, brand: e.target.value})}>
                    <option value="">بدون برند</option>{brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                  </select>
                </FormGroup>
                <FormGroup><label>وضعیت فیزیکی</label>
                  <select value={productForm.condition} onChange={e => setProductForm({...productForm, condition: e.target.value})}>
                    <option value="new">نو (New)</option><option value="used">دست دوم (Used)</option>
                  </select>
                </FormGroup>
                <FormGroup><label>شماره مدل</label><input value={productForm.model_number} onChange={e => setProductForm({...productForm, model_number: e.target.value})} dir="ltr" /></FormGroup>
                <FormGroup><label>هشدار موجودی کم</label><input type="number" min="0" value={productForm.min_stock_alert} onChange={e => setProductForm({...productForm, min_stock_alert: parseInt(e.target.value)})} /></FormGroup>
                <FormGroup style={{ flexDirection: 'row', alignItems: 'center', marginTop: '2rem' }}>
                  <input type="checkbox" checked={productForm.is_active} onChange={e => setProductForm({...productForm, is_active: e.target.checked})} style={{ width: '20px', height: '20px' }} />
                  <label style={{ margin: 0 }}>کالا فعال باشد</label>
                </FormGroup>
                <FormGroup className="full-width"><label>توضیحات داخلی</label><textarea value={productForm.description} onChange={e => setProductForm({...productForm, description: e.target.value})} /></FormGroup>
              </FormGrid>
              <ModalActions>
                <button type="button" className="cancel" onClick={() => setShowProductModal(false)}>انصراف</button>
                <button type="submit" className="submit" disabled={submitting}>{submitting ? 'در حال ثبت...' : 'ذخیره کالا'}</button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}

      {/* Modal: Publish to Market */}
      {publishModalObj && (
        <ModalOverlay onClick={(e) => { if(e.target === e.currentTarget) setPublishModalObj(null); }}>
          <ModalContent style={{ maxWidth: '600px' }}>
            <h2 style={{ marginBottom: '1.5rem', color: 'var(--textMain)' }}>انتشار در فروشگاه: {publishModalObj.name}</h2>

            <div style={{ marginBottom: '1.5rem', fontSize: '0.9rem', color: 'var(--textMuted)' }}>
              موجودی آزاد در انبار: <strong style={{ color: 'var(--success)' }}>{publishModalObj.available_stock} عدد</strong>
            </div>

            <form onSubmit={handlePublishSubmit}>
              <FormGrid>
                <FormGroup>
                  <label>تعداد برای فروش در سایت *</label>
                  <input type="number" min="1" max={publishModalObj.available_stock} required
                         value={publishForm.market_quantity}
                         onChange={(e) => setPublishForm({...publishForm, market_quantity: e.target.value})} />
                </FormGroup>

                <FormGroup>
                  <label>قیمت فروش (تومان)</label>
                  <input type="number" placeholder="مثال: 5000000"
                         value={publishForm.market_price}
                         onChange={(e) => setPublishForm({...publishForm, market_price: e.target.value})} />
                </FormGroup>

                <FormGroup className="full-width">
                  <label>تگ‌های جستجو (با کاما جدا کنید)</label>
                  <input type="text" placeholder="مثال: سرور, HP, G10"
                         value={publishForm.market_tags}
                         onChange={(e) => setPublishForm({...publishForm, market_tags: e.target.value})} />
                </FormGroup>

                <FormGroup className="full-width">
                  <label>توضیحات کوتاه برای ویترین فروشگاه</label>
                  <textarea
                    value={publishForm.market_description}
                    onChange={(e) => setPublishForm({...publishForm, market_description: e.target.value})}
                    style={{ minHeight: '80px', resize: 'vertical' }}
                    placeholder="این توضیحات در صفحه محصول به مشتری نمایش داده می‌شود..."
                  />
                </FormGroup>
              </FormGrid>

              <ModalActions>
                <button type="button" className="cancel" onClick={() => setPublishModalObj(null)}>انصراف</button>
                <button type="submit" className="submit" disabled={submitting}>
                  {submitting ? 'در حال ارتباط با مارکت...' : 'تایید و انتشار نهایی'}
                </button>
              </ModalActions>
            </form>
          </ModalContent>
        </ModalOverlay>
      )}
    </PageWrapper>
  );
}