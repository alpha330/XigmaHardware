'use client';

import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { faStar, faCheckCircle, faTimesCircle } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
`;

const ReviewCard = styled.div`
  background: ${p => p.theme.colors.surface.card};
  border: 1px solid ${p => p.theme.colors.border.light};
  border-radius: ${p => p.theme.borderRadius.lg};
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const ProductInfo = styled.div`
  font-weight: 600;
  font-size: 1rem;
`;

const Date = styled.div`
  font-size: 0.8rem;
  color: ${p => p.theme.colors.text.muted};
`;

const Rating = styled.div`
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 10px;
`;

const Text = styled.p`
  color: ${p => p.theme.colors.text.secondary};
  font-size: 0.9rem;
  line-height: 1.7;
`;

const Tags = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
`;

const Tag = styled.span`
  padding: 3px 10px;
  border-radius: 50px;
  font-size: 0.75rem;
  background: ${p => p.$positive ? '#ecfdf5' : '#fef2f2'};
  color: ${p => p.$positive ? '#059669' : '#dc2626'};
  display: flex;
  align-items: center;
  gap: 4px;
`;

const VerifiedBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.75rem;
  margin-left: 8px;
`;

export const ReviewsList = ({ reviews }) => {
  if (reviews.length === 0) {
    return <p style={{ color: '#94a3b8' }}>هنوز نظری ثبت نکرده‌اید.</p>;
  }

  return (
    <Grid>
      {reviews.map(review => (
        <ReviewCard key={review.id}>
          <Header>
            <div>
              <ProductInfo>
                {review.product_name || review.product}
                {review.is_verified_purchase && (
                  <VerifiedBadge>
                    <Icon icon={faCheckCircle} size="xs" /> خرید تأیید شده
                  </VerifiedBadge>
                )}
              </ProductInfo>
              <Date>{review.created_at}</Date>
            </div>
          </Header>

          {review.rating_overall && (
            <Rating>
              {[1,2,3,4,5].map(i => (
                <Icon
                  key={i}
                  icon={faStar}
                  size="sm"
                  color={i <= review.rating_overall ? '#f59e0b' : '#e2e8f0'}
                />
              ))}
            </Rating>
          )}

          <Text>{review.body || review.text}</Text>

          {(review.pros_list?.length > 0 || review.cons_list?.length > 0) && (
            <Tags>
              {review.pros_list?.slice(0, 3).map((pro, i) => (
                <Tag key={`pro-${i}`} $positive>
                  <Icon icon={faCheckCircle} size="xs" /> {pro}
                </Tag>
              ))}
              {review.cons_list?.slice(0, 2).map((con, i) => (
                <Tag key={`con-${i}`} $positive={false}>
                  <Icon icon={faTimesCircle} size="xs" /> {con}
                </Tag>
              ))}
            </Tags>
          )}
        </ReviewCard>
      ))}
    </Grid>
  );
};