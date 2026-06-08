'use client';

import styled from '@emotion/styled';
import { Icon } from '@/components/ui/Icon';
import { faWallet, faArrowUp, faArrowDown } from '@fortawesome/free-solid-svg-icons';

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
`;

const BalanceCard = styled.div`
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  color: white;
  border-radius: 16px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const BalanceLabel = styled.div`
  font-size: 0.9rem;
  opacity: 0.8;
`;

const BalanceAmount = styled.div`
  font-size: 2.5rem;
  font-weight: 800;
`;

const BalanceSub = styled.div`
  font-size: 0.85rem;
  opacity: 0.7;
  display: flex;
  gap: 24px;
`;

const TxList = styled.div`
  max-height: 400px;
  overflow-y: auto;
`;

const TxItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid ${p => p.theme.colors.border.light};
`;

export const WalletCard = ({ wallet, transactions }) => {
  const balance = wallet?.balance || wallet?.wallet?.balance || 0;
  const blocked = wallet?.blocked_balance || wallet?.wallet?.blocked_balance || 0;

  return (
    <Grid>
      <BalanceCard>
        <BalanceLabel><Icon icon={faWallet} /> موجودی قابل برداشت</BalanceLabel>
        <BalanceAmount>{balance?.toLocaleString()} <span style={{ fontSize: '0.9rem' }}>تومان</span></BalanceAmount>
        <BalanceSub>
          <span>مسدود: {blocked?.toLocaleString()}</span>
          <span>کل: {(balance + blocked)?.toLocaleString()}</span>
        </BalanceSub>
      </BalanceCard>

      <div>
        <h3 style={{ fontWeight: 600, marginBottom: 16 }}>تراکنش‌های اخیر</h3>
        <TxList>
          {transactions.map(tx => (
            <TxItem key={tx.id}>
              <Icon icon={tx.transaction_type === 'deposit' ? faArrowDown : faArrowUp}
                    color={tx.transaction_type === 'deposit' ? '#059669' : '#dc2626'} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{tx.description || tx.transaction_type}</div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{tx.created_at}</div>
              </div>
              <div style={{ fontWeight: 600, color: tx.transaction_type === 'deposit' ? '#059669' : '#dc2626' }}>
                {tx.transaction_type === 'deposit' ? '+' : '-'}{tx.amount?.toLocaleString()}
              </div>
            </TxItem>
          ))}
        </TxList>
      </div>
    </Grid>
  );
};