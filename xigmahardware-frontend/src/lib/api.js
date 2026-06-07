// src/lib/api.js
'use server';

import { cookies } from 'next/headers';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * توابع سرور-ساید برای ارتباط با API
 * تمام درخواست‌ها در سرور انجام میشه و نتیجه به کلاینت برمیگرده
 */

// ==================== Helper ====================

async function getAuthHeaders() {
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;

  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    return {
      success: false,
      error: data.error || data.detail || 'خطایی رخ داده است.',
      status: response.status,
      data: null,
    };
  }

  return {
    success: true,
    error: null,
    status: response.status,
    data,
  };
}

// ==================== Generic Methods ====================

export async function apiGet(endpoint, options = {}) {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers,
      cache: options.cache || 'no-store',
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    return { success: false, error: 'خطا در ارتباط با سرور.', data: null };
  }
}

export async function apiPost(endpoint, body = {}, options = {}) {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    return { success: false, error: 'خطا در ارتباط با سرور.', data: null };
  }
}

export async function apiPut(endpoint, body = {}, options = {}) {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    return { success: false, error: 'خطا در ارتباط با سرور.', data: null };
  }
}

export async function apiPatch(endpoint, body = {}, options = {}) {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(body),
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    return { success: false, error: 'خطا در ارتباط با سرور.', data: null };
  }
}

export async function apiDelete(endpoint, options = {}) {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers,
      ...options,
    });
    return await handleResponse(response);
  } catch (error) {
    return { success: false, error: 'خطا در ارتباط با سرور.', data: null };
  }
}

// ==================== Auth Specific ====================

export async function loginUser(credentials) {
  return await apiPost('/accounts/auth/login/', credentials);
}

export async function registerUser(userData) {
  const endpoint = userData.email
    ? '/accounts/auth/register/email/'
    : '/accounts/auth/register/mobile/';
  return await apiPost(endpoint, userData);
}

export async function refreshToken() {
  const cookieStore = await cookies();
  const refresh = cookieStore.get('refresh_token')?.value;
  if (!refresh) return { success: false, error: 'No refresh token.' };

  return await apiPost('/accounts/auth/token/refresh/', { refresh });
}

export async function logoutUser() {
  const cookieStore = await cookies();
  const refresh = cookieStore.get('refresh_token')?.value;

  await apiPost('/accounts/auth/logout/', { refresh });
  await apiPost('/accounts/auth/token/blacklist/', { refresh });
}

// ==================== User ====================

export async function getCurrentUser() {
  return await apiGet('/accounts/me/');
}

export async function updateProfile(data) {
  return await apiPatch('/accounts/me/', data);
}

// ==================== Products ====================

export async function getProducts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/market/products/${query ? `?${query}` : ''}`);
}

export async function getProduct(slug) {
  return await apiGet(`/market/products/?slug=${slug}`);
}

// ==================== Cart ====================

export async function getCart() {
  return await apiGet('/basket/carts/my_cart/');
}

export async function addToCart(productId, quantity = 1) {
  return await apiPost('/basket/carts/add_item/', { product_id: productId, quantity });
}

export async function removeFromCart(itemId) {
  return await apiPost(`/basket/carts/remove-item/${itemId}/`);
}

// ==================== Wishlist ====================

export async function getWishlists() {
  return await apiGet('/basket/wishlists/');
}

export async function createWishlist(name) {
  return await apiPost('/basket/wishlists/', { name });
}

// ==================== Wallet ====================

export async function getWallet() {
  return await apiGet('/accounts/me/wallet/');
}

export async function depositWallet(amount) {
  return await apiPost('/accounts/me/wallet/deposit/', { amount });
}

// ==================== Orders/Invoices ====================

export async function getInvoices(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/financial/invoices/my_invoices/${query ? `?${query}` : ''}`);
}

// ==================== Support ====================

export async function getTickets() {
  return await apiGet('/support/tickets/my_tickets/');
}

export async function createTicket(data) {
  return await apiPost('/support/tickets/', data);
}

export async function replyTicket(ticketId, body) {
  return await apiPost(`/support/tickets/${ticketId}/reply/`, { body });
}

// ==================== Addresses ====================

export async function getAddresses() {
  return await apiGet('/logistics/addresses/');
}

export async function createAddress(data) {
  return await apiPost('/logistics/addresses/', data);
}

// ==================== Ratings & Reviews ====================

export async function reviewProduct(productId, review) {
  return await apiPost('/market/reviews/', { product: productId, ...review });
}

// src/lib/api.js
// ==================== اضافه کردن به انتهای فایل ====================

// ==================== Auth - OTP ====================

export async function requestOTP(mobile, purpose = 'login') {
  return await apiPost('/accounts/auth/otp/request/', {
    mobile,
    purpose
  });
}

export async function verifyOTP(mobile, code) {
  return await apiPost('/accounts/auth/otp/verify/', {
    mobile,
    code
  });
}

export async function resetPasswordRequest(emailOrMobile) {
  return await apiPost('/accounts/auth/password/reset/', {
    email_or_mobile: emailOrMobile
  });
}

export async function resetPasswordConfirm(emailOrMobile, code, newPassword) {
  return await apiPost('/accounts/auth/password/reset/confirm/', {
    email_or_mobile: emailOrMobile,
    code,
    new_password: newPassword,
    new_password_confirm: newPassword,
  });
}

export async function changePassword(oldPassword, newPassword) {
  return await apiPost('/accounts/auth/password/change/', {
    old_password: oldPassword,
    new_password: newPassword,
    new_password_confirm: newPassword,
  });
}

export async function verifyEmail(token) {
  return await apiGet(`/accounts/auth/verify/email/${token}/`);
}

export async function resendVerificationEmail() {
  return await apiPost('/accounts/auth/verify/email/resend/');
}

// ==================== Profile ====================

export async function getMyProfile() {
  return await apiGet('/accounts/me/profile/');
}

export async function updateMyProfile(data) {
  return await apiPatch('/accounts/me/profile/', data);
}

export async function switchToLegal(data) {
  return await apiPost('/accounts/me/profile/switch-to-legal/', data);
}

export async function switchToIndividual(data) {
  return await apiPost('/accounts/me/profile/switch-to-individual/', data);
}

// ==================== Addresses ====================

export async function getMyAddresses() {
  return await apiGet('/logistics/addresses/');
}

export async function createMyAddress(data) {
  return await apiPost('/logistics/addresses/', data);
}

export async function updateMyAddress(id, data) {
  return await apiPatch(`/logistics/addresses/${id}/`, data);
}

export async function deleteMyAddress(id) {
  return await apiDelete(`/logistics/addresses/${id}/`);
}

export async function setDefaultAddress(id) {
  return await apiPost(`/logistics/addresses/${id}/set_default/`);
}

export async function getDefaultAddress() {
  return await apiGet('/logistics/addresses/default/');
}

// ==================== Wallet ====================

export async function getMyWallet() {
  return await apiGet('/accounts/me/wallet/');
}

export async function depositToWallet(amount, description = '') {
  return await apiPost('/accounts/me/wallet/deposit/', { amount, description });
}

export async function withdrawFromWallet(amount, description = '') {
  return await apiPost('/accounts/me/wallet/withdraw/', { amount, description });
}

export async function getWalletTransactions(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/accounts/me/wallet/transactions/${query ? `?${query}` : ''}`);
}

// ==================== Market Products ====================

export async function getMarketProducts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/market/products/${query ? `?${query}` : ''}`);
}

export async function getMarketProduct(idOrSlug) {
  return await apiGet(`/market/products/${idOrSlug}/`);
}

export async function getFeaturedProducts() {
  return await apiGet('/market/products/featured/');
}

export async function getBestsellers() {
  return await apiGet('/market/products/bestsellers/');
}

export async function getNewArrivals() {
  return await apiGet('/market/products/new_arrivals/');
}

export async function searchProducts(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/market/products/search/${query ? `?${query}` : ''}`);
}

export async function compareProducts(ids) {
  return await apiGet(`/market/products/compare/?ids=${ids.join(',')}`);
}

export async function getRelatedProducts(productId) {
  return await apiGet(`/market/products/${productId}/related/`);
}

// ==================== Ratings & Reviews ====================

export async function getProductRatings(productId) {
  return await apiGet(`/market/ratings/?product=${productId}`);
}

export async function getRatingSummary(productId) {
  return await apiGet(`/market/ratings/summary/?product=${productId}`);
}

export async function rateProduct(productId, rating) {
  return await apiPost('/market/ratings/', {
    product: productId,
    value_for_money: rating.valueForMoney,
    quality: rating.quality,
    performance: rating.performance,
    overall: rating.overall,
  });
}

export async function getMyRating(productId) {
  return await apiGet(`/market/ratings/my_rating/?product=${productId}`);
}

export async function getProductReviews(productId, params = {}) {
  const query = new URLSearchParams({ product: productId, ...params }).toString();
  return await apiGet(`/market/reviews/?${query}`);
}

export async function createReview(productId, data) {
  return await apiPost('/market/reviews/', { product: productId, ...data });
}

export async function likeReview(reviewId, isLike = true) {
  return await apiPost(`/market/reviews/${reviewId}/like/`, { is_like: isLike });
}

export async function getMyReview(productId) {
  return await apiGet(`/market/reviews/my_review/?product=${productId}`);
}

// ==================== Comments ====================

export async function getProductComments(productId, params = {}) {
  const query = new URLSearchParams({ product: productId, ...params }).toString();
  return await apiGet(`/market/comments/?${query}`);
}

export async function createComment(productId, body, parentId = null) {
  return await apiPost('/market/comments/', {
    product: productId,
    body,
    parent: parentId,
  });
}

// ==================== Cart ====================

export async function getMyCart() {
  return await apiGet('/basket/carts/my_cart/');
}


export async function updateCartItem(itemId, quantity) {
  return await apiPost(`/basket/carts/update-item/${itemId}/`, { quantity });
}

export async function removeCartItem(itemId) {
  return await apiPost(`/basket/carts/remove-item/${itemId}/`);
}

export async function removeSelectedCartItems(cartId, itemIds) {
  return await apiPost(`/basket/carts/${cartId}/remove_selected/`, { item_ids: itemIds });
}

export async function clearCart(cartId) {
  return await apiPost(`/basket/carts/${cartId}/clear_cart/`);
}

export async function getCartSummary(cartId) {
  return await apiGet(`/basket/carts/${cartId}/summary/`);
}

// ==================== Wishlist ====================

export async function getMyWishlists() {
  return await apiGet('/basket/wishlists/');
}

export async function updateWishlist(id, data) {
  return await apiPatch(`/basket/wishlists/${id}/`, data);
}

export async function deleteWishlist(id) {
  return await apiDelete(`/basket/wishlists/${id}/`);
}

export async function addToWishlist(wishlistId, productId, quantity = 1) {
  return await apiPost(`/basket/wishlists/${wishlistId}/add_item/`, {
    product_id: productId,
    quantity,
  });
}

export async function convertWishlistToCart(wishlistId) {
  return await apiPost(`/basket/wishlists/${wishlistId}/convert_to_cart/`);
}

export async function duplicateWishlist(wishlistId) {
  return await apiPost(`/basket/wishlists/${wishlistId}/duplicate/`);
}

export async function setWishlistDiscount(wishlistId, percent, note = '') {
  return await apiPost(`/basket/wishlists/${wishlistId}/set_discount/`, {
    discount_percent: percent,
    note,
  });
}

export async function getWishlistBudgetAnalysis(wishlistId) {
  return await apiGet(`/basket/wishlists/${wishlistId}/budget_analysis/`);
}

// ==================== Invoices ====================

export async function getMyInvoices(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/financial/invoices/my_invoices/${query ? `?${query}` : ''}`);
}

export async function getInvoice(id) {
  return await apiGet(`/financial/invoices/${id}/`);
}

export async function createInvoiceFromCart(paymentMethod = 'wallet') {
  return await apiPost('/financial/invoices/create_from_cart/', {
    payment_method: paymentMethod,
  });
}

export async function walletCharge(amount) {
  return await apiPost('/financial/invoices/wallet_charge/', { amount });
}

// ==================== Support ====================

export async function getMyTickets(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/support/tickets/my_tickets/${query ? `?${query}` : ''}`);
}


export async function getTicket(id) {
  return await apiGet(`/support/tickets/${id}/`);
}

export async function replyToTicket(ticketId, body) {
  return await apiPost(`/support/tickets/${ticketId}/reply/`, { body });
}

export async function updateTicketStatus(ticketId, status) {
  return await apiPost(`/support/tickets/${ticketId}/update_status/`, { status });
}

// ==================== Warranty ====================

export async function getMyWarranties() {
  return await apiGet('/support/warranties/my_warranties/');
}

export async function checkWarranty(serialNumber) {
  return await apiGet(`/support/warranties/check/?serial=${serialNumber}`);
}

export async function claimWarranty(warrantyId, description) {
  return await apiPost(`/support/warranties/${warrantyId}/claim/`, { description });
}

// ==================== Chat ====================

export async function startChat(subject = '', message = '') {
  return await apiPost('/support/chats/start/', { subject, message });
}

export async function sendChatMessage(chatId, message) {
  return await apiPost(`/support/chats/${chatId}/send/`, { message });
}

export async function closeChat(chatId) {
  return await apiPost(`/support/chats/${chatId}/close/`);
}

// ==================== Shipment Tracking ====================

export async function getMyShipments(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/logistics/shipments/my_shipments/${query ? `?${query}` : ''}`);
}

export async function getShipment(id) {
  return await apiGet(`/logistics/shipments/${id}/`);
}

export async function trackShipment(id) {
  return await apiGet(`/logistics/shipments/${id}/tracking/`);
}

export async function cancelShipment(id, reason = '') {
  return await apiPost(`/logistics/shipments/${id}/cancel/`, { reason });
}

// ==================== Payment ====================

export async function createPayment(amount, description = '') {
  return await apiPost('/payment/pay/', { amount, description });
}

export async function payWithWallet(amount, description = '') {
  return await apiPost('/payment/pay/wallet/', { amount, description });
}

export async function verifyPayment(paymentLogId) {
  return await apiPost(`/payment/verify/${paymentLogId}/`);
}

export async function getPaymentStatus(paymentLogId) {
  return await apiGet(`/payment/status/${paymentLogId}/`);
}

export async function getActiveGateways() {
  return await apiGet('/payment/active-gateways/');
}

// ==================== Website ====================

export async function getPages(type = '') {
  const query = type ? `?type=${type}` : '';
  return await apiGet(`/website/pages/${query}`);
}

export async function getArticles(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/website/articles/${query ? `?${query}` : ''}`);
}

export async function getArticle(slug) {
  return await apiGet(`/website/articles/${slug}/`);
}

export async function getFeaturedArticles() {
  return await apiGet('/website/articles/featured/');
}

export async function getNews(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/website/news/${query ? `?${query}` : ''}`);
}

export async function getPinnedNews() {
  return await apiGet('/website/news/pinned/');
}

export async function submitContact(data) {
  return await apiPost('/website/contact/', data);
}

export async function subscribeNewsletter(email) {
  return await apiPost('/website/newsletter/subscribe/', { email });
}

export async function unsubscribeNewsletter(email) {
  return await apiPost('/website/newsletter/unsubscribe/', { email });
}

// ==================== FAQ ====================

export async function getFAQs(params = {}) {
  const query = new URLSearchParams(params).toString();
  return await apiGet(`/support/faqs/${query ? `?${query}` : ''}`);
}

export async function getFAQCategories() {
  return await apiGet('/support/faqs/categories/');
}

export async function markFAQHelpful(faqId) {
  return await apiPost(`/support/faqs/${faqId}/helpful/`);
}

// ==================== Brands & Categories ====================

export async function getBrands() {
  return await apiGet('/stock/brands/');
}

export async function getCategories() {
  return await apiGet('/stock/categories/');
}

export async function getCategoryTree() {
  return await apiGet('/stock/categories/tree/');
}

// ==================== Logistics Cost ====================

export async function estimateShippingCost(data) {
  return await apiPost('/logistics/shipments/cost_estimate/', data);
}