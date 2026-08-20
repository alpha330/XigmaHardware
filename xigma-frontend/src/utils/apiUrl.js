const normalizeBaseUrl = (value) => (value || '').replace(/\/+$/, '');

export const publicApiBaseUrl = normalizeBaseUrl(
  process.env.NEXT_PUBLIC_API_URL,
);

export const apiUrl = (endpoint) => {
  if (/^https?:\/\//i.test(endpoint)) return endpoint;

  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${publicApiBaseUrl}${path}`;
};
