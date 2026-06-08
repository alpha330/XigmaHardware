// src/lib/api.js
'use server';

import { cookies } from 'next/headers';

const API_BASE = process.env.API_URL || 'http://localhost:8000/api/v1';

async function getHeaders() {
  const c = await cookies();
  const token = c.get('access_token')?.value;
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

async function request(method, endpoint, body, options = {}) {
  try {
    const headers = await getHeaders();
    const res = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache: options.cache || 'no-store',
      ...options,
    });
    const data = await res.json();
    if (!res.ok) return { success: false, error: data.error || data.detail || 'خطا', status: res.status, data: null };
    return { success: true, error: null, status: res.status, data };
  } catch (e) {
    return { success: false, error: 'خطا در ارتباط با سرور', data: null };
  }
}

// ==================== Helper ====================
async function get(endpoint, options) { return request('GET', endpoint, null, options); }
async function post(endpoint, body, options) { return request('POST', endpoint, body, options); }
async function put(endpoint, body, options) { return request('PUT', endpoint, body, options); }
async function patch(endpoint, body, options) { return request('PATCH', endpoint, body, options); }
async function del(endpoint, options) { return request('DELETE', endpoint, null, options); }

// ==================== Auth ====================
export async function loginUser(d) { return post('/accounts/auth/login/', d); }
export async function registerUser(d) { return post(d.email ? '/accounts/auth/register/email/' : '/accounts/auth/register/mobile/', d); }
export async function requestOTP(m, p = 'login') { return post('/accounts/auth/otp/request/', { mobile: m, purpose: p }); }
export async function resetPassword(d) { return post('/accounts/auth/password/reset/', d); }
export async function resetPasswordConfirm(d) { return post('/accounts/auth/password/reset/confirm/', d); }

// ==================== Products ====================
export async function getProducts(p = {}) { return get(`/market/products/?${new URLSearchParams(p)}`); }
export async function getProduct(slug) { return get(`/market/products/?slug=${slug}`); }
export async function getFeatured() { return get('/market/products/featured/'); }
export async function getBestsellers() { return get('/market/products/bestsellers/'); }
export async function searchProducts(p) { return get(`/market/products/search/?${new URLSearchParams(p)}`); }

// ==================== Cart ====================
export async function getCart() { return get('/basket/carts/my_cart/'); }
export async function addToCart(pid, q = 1) { return post('/basket/carts/add_item/', { product_id: pid, quantity: q }); }
export async function removeCartItem(id) { return post(`/basket/carts/remove-item/${id}/`); }
export async function updateCartItem(id, q) { return post(`/basket/carts/update-item/${id}/`, { quantity: q }); }
export async function clearCart(cartId) { return post(`/basket/carts/${cartId}/clear_cart/`); }

// ==================== User ====================
export async function getMe() { return get('/accounts/me/'); }
export async function updateProfile(d) { return patch('/accounts/me/', d); }
export async function getWallet() { return get('/accounts/me/wallet/'); }
export async function getWalletTransactions(p = {}) { return get(`/accounts/me/wallet/transactions/?${new URLSearchParams(p)}`); }
export async function getAddresses() { return get('/logistics/addresses/'); }
export async function createAddress(d) { return post('/logistics/addresses/', d); }
export async function setDefaultAddress(id) { return post(`/logistics/addresses/${id}/set_default/`); }

// ==================== Reviews & Ratings ====================
export async function getReviews(pid) { return get(`/market/reviews/?product=${pid}`); }
export async function rateProduct(pid, r) { return post('/market/ratings/', { product: pid, ...r }); }
export async function createReview(pid, d) { return post('/market/reviews/', { product: pid, ...d }); }

// ==================== Support ====================
export async function getTickets() { return get('/support/tickets/my_tickets/'); }
export async function createTicket(d) { return post('/support/tickets/', d); }
export async function getFAQs() { return get('/support/faqs/'); }
export async function getFAQCategories() { return get('/support/faqs/categories/'); }
export async function createFAQ(d) { return post('/support/faqs/', d); }
export async function updateFAQ(id, d) { return put(`/support/faqs/${id}/`, d); }
export async function deleteFAQ(id) { return del(`/support/faqs/${id}/`); }

// ==================== Warranty ====================
export async function getWarranties() { return get('/support/warranties/'); }
export async function checkWarranty(serial) { return get(`/support/warranties/check/?serial=${serial}`); }

// ==================== Chat ====================
export async function getActiveChats() { return get('/support/chats/active/'); }
export async function startChat(subj, msg) { return post('/support/chats/start/', { subject: subj, message: msg }); }
export async function sendChatMsg(id, msg) { return post(`/support/chats/${id}/send/`, { message: msg }); }
export async function closeChat(id) { return post(`/support/chats/${id}/close/`); }

// ==================== Invoices & Transactions ====================
export async function getMyInvoices(p = {}) { return get(`/financial/invoices/my_invoices/?${new URLSearchParams(p)}`); }
export async function getInvoices(p = {}) { return get(`/financial/invoices/?${new URLSearchParams(p)}`); }
export async function createInvoiceFromCart(pm = 'wallet') { return post('/financial/invoices/create_from_cart/', { payment_method: pm }); }
export async function walletCharge(amount) { return post('/financial/invoices/wallet_charge/', { amount }); }
export async function getTransactions(p = {}) { return get(`/financial/transactions/?${new URLSearchParams(p)}`); }
export async function getReports() { return get('/financial/reports/'); }

// ==================== Payment ====================
export async function createPayment(amount, desc = '') { return post('/payment/pay/', { amount, description: desc }); }
export async function payWithWallet(amount, desc = '') { return post('/payment/pay/wallet/', { amount, description: desc }); }
export async function verifyPayment(logId) { return post(`/payment/verify/${logId}/`); }

// ==================== Logistics ====================
export async function getMyShipments() { return get('/logistics/shipments/my_shipments/'); }
export async function getShipment(id) { return get(`/logistics/shipments/${id}/`); }
export async function trackShipment(id) { return get(`/logistics/shipments/${id}/tracking/`); }
export async function cancelShipment(id, reason = '') { return post(`/logistics/shipments/${id}/cancel/`, { reason }); }
export async function getCouriers(p = {}) { return get(`/logistics/couriers/?${new URLSearchParams(p)}`); }
export async function updateCourierStatus(id) { return post(`/logistics/couriers/${id}/toggle_available/`); }

// ==================== Gateways ====================
export async function getGateways() { return get('/payment/gateways/'); }
export async function toggleGatewayActive(id) { return post(`/payment/gateways/${id}/toggle_active/`); }
export async function setGatewayDefault(id) { return post(`/payment/gateways/${id}/set_default/`); }

// ==================== Discounts ====================
export async function getWishlists() { return get('/basket/wishlists/'); }
export async function setWishlistDiscount(id, percent) { return post(`/basket/wishlists/${id}/set_discount/`, { discount_percent: percent }); }
export async function clearDiscount(id) { return post(`/basket/wishlists/${id}/clear_discount/`); }

// ==================== Website ====================
export async function getNews() { return get('/website/news/'); }
export async function getArticles() { return get('/website/articles/'); }
export async function submitContact(d) { return post('/website/contact/', d); }
export async function subscribeNewsletter(email) { return post('/website/newsletter/subscribe/', { email }); }

// ==================== Brands & Categories ====================
export async function getBrands() { return get('/stock/brands/'); }
export async function getCategories() { return get('/stock/categories/'); }
export async function getCategoryTree() { return get('/stock/categories/tree/'); }

export async function getInventoryItems(p = {}) {
  return get(`/stock/inventory/?${new URLSearchParams(p)}`);
}
export async function addStock(itemId, qty) {
  return post(`/stock/inventory/${itemId}/add_stock/`, { quantity: qty });
}
export async function removeStock(itemId, qty) {
  return post(`/stock/inventory/${itemId}/remove_stock/`, { quantity: qty });
}
export async function transferStock(itemId, toWarehouseId, qty) {
  return post(`/stock/inventory/${itemId}/transfer/`, {
    to_warehouse: toWarehouseId,
    quantity: qty
  });
}


export async function getMyReviews() {
  return get('/market/reviews/my_review/');
}

// Users (admin)
export async function getUsersList(p = {}) {
  return get(`/accounts/users/?${new URLSearchParams(p)}`);
}
export async function updateUserRole(userId, role) {
  return post(`/accounts/users/${userId}/change_role/`, { role });
}
export async function toggleUserActive(userId) {
  return post(`/accounts/users/${userId}/toggle_active/`);
}

// Wishlists (already have getWishlists, convertWishlistToCart, deleteWishlist)getMyTickets
export async function convertWishlistToCart(id) {
  return post(`/basket/wishlists/${id}/convert_to_cart/`);
}
export async function deleteWishlist(id) {
  return del(`/basket/wishlists/${id}/`);
}

export async function getMyTickets() {
  return get('/support/tickets/my_tickets/');
}