import styled from '@emotion/styled';

const TimerWrapper = styled.div`
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Circle = styled.circle`
  transition: stroke-dashoffset 1s linear;
  stroke: ${({ theme }) => theme.colors.primary};
  stroke-width: 4;
  fill: transparent;
`;

export default function CircularTimer({ timeLeft }) {
  const radius = 25;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (timeLeft / 120) * circumference;

  return (
    <TimerWrapper>
      <svg width="60" height="60" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="30" cy="30" r={radius} stroke="#e0e0e0" strokeWidth="4" fill="transparent" />
        <Circle cx="30" cy="30" r={radius} strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" />
      </svg>
      <span style={{ position: 'absolute', fontSize: '0.9rem' }}>
        {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
      </span>
    </TimerWrapper>
  );
}