import Cookies from 'js-cookie';


const cookieOptions = () => ({
  path: '/',
  sameSite: 'strict',
  secure: typeof window !== 'undefined' && window.location.protocol === 'https:',
});

export const storeAuthTokens = (tokens) => {
  Cookies.set('token', tokens.access, {
    ...cookieOptions(),
    expires: 1 / 24,
  });
  Cookies.set('refresh', tokens.refresh, {
    ...cookieOptions(),
    expires: 7,
  });
};

export const clearAuthTokens = () => {
  Cookies.remove('token', cookieOptions());
  Cookies.remove('refresh', cookieOptions());
};
