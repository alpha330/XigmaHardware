import 'server-only';

const serverApiBaseUrl = (
  process.env.API_URL
  || process.env.NEXT_PUBLIC_API_URL
  || 'http://localhost:8000'
).replace(/\/+$/, '');

export const serverApiUrl = (endpoint) => {
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${serverApiBaseUrl}${path}`;
};
