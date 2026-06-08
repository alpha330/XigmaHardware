import { getWallet, getWalletTransactions } from '@/lib/api';
import { WalletCard } from '@/components/dashboard/WalletCard';
import { Button } from '@/components/ui/Button';

export default async function WalletPage() {
  const [walletRes, txRes] = await Promise.all([
    getWallet(),
    getWalletTransactions({ limit: 20 })
  ]);

  return (
    <div className="animate-fade-in-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>💰 کیف پول</h1>
        <Button variant="primary" onClick={() => window.location.href = '/dashboard/wallet/charge'}>
          شارژ کیف پول
        </Button>
      </div>
      <WalletCard
        wallet={walletRes.data}
        transactions={txRes.data?.results || []}
      />
    </div>
  );
}