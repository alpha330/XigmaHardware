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

const Track = styled.circle`
  stroke: ${({ theme }) => theme.colors.borderStrong};
  stroke-width: 4;
  fill: transparent;
`;

const TimerText = styled.span`
  position: absolute;
  color: ${({ theme }) => theme.colors.textMain};
  font-size: 0.9rem;
  font-variant-numeric: tabular-nums;
`;

export default function CircularTimer({ timeLeft }) {
  const radius = 25;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (timeLeft / 120) * circumference;

  return (
    <TimerWrapper>
      <svg width="60" height="60" aria-hidden="true" style={{ transform: 'rotate(-90deg)' }}>
        <Track cx="30" cy="30" r={radius} />
        <Circle cx="30" cy="30" r={radius} strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" />
      </svg>
      <TimerText aria-label={`${timeLeft} ثانیه تا امکان ارسال مجدد`}>
        {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
      </TimerText>
    </TimerWrapper>
  );
}
