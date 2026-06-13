export function formatPrice(price) {
  return Number(price).toLocaleString('fa-IR');
}

export function formatToman(price) {
  return `${formatPrice(price)} تومان`;
}