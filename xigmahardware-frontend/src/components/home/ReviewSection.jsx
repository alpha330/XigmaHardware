'use client';
import styled from '@emotion/styled';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faStar } from '@fortawesome/free-solid-svg-icons';

const Section = styled.section`
  padding: 3rem 1rem;
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.colors.text};
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
`;

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.radius};
  box-shadow: ${({ theme }) => theme.shadows.sm};
`;

const Stars = styled.div`
  color: #f59e0b;
  margin-bottom: 0.5rem;
`;

export default function ReviewSection({ reviews = [] }) {
  return (
    <Section>
      <Title>نظرات مشتریان</Title>
      <Grid>
        {reviews.slice(0, 6).map(review => (
          <Card key={review.id}>
            <h4>{review.title}</h4>
            <Stars>
              {Array.from({ length: review.rating_overall || 5 }, (_, i) => (
                <FontAwesomeIcon key={i} icon={faStar} />
              ))}
            </Stars>
            <p>{review.body_short || review.body?.substring(0, 120)}...</p>
            <small>— {review.user_name}</small>
          </Card>
        ))}
      </Grid>
    </Section>
  );
}