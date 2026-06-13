import moment from 'moment-jalaali';

export function toJalali(date) {
  return moment(date).format('jYYYY/jMM/jDD');
}

export function toJalaliDateTime(date) {
  return moment(date).format('jYYYY/jMM/jDD HH:mm');
}

export function getCurrentJalaliDate() {
  return moment().format('jYYYY/jMM/jDD');
}