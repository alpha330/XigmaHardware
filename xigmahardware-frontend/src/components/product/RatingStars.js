import { Icon } from '@/components/ui/Icon';
import { faStar, faStarHalfStroke } from '@fortawesome/free-solid-svg-icons';

export const RatingStars = ({ rating, count }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 4, margin: '12px 0' }}>
    {[1,2,3,4,5].map(i => (
      <Icon key={i} icon={i <= Math.floor(rating) ? faStar : i <= rating ? faStarHalfStroke : faStar} size="sm" color={i <= rating ? '#f59e0b' : '#cbd5e1'} />
    ))}
    {count != null && <span style={{ fontSize: '0.85rem', color: '#94a3b8', marginRight: 8 }}>({count})</span>}
  </div>
);