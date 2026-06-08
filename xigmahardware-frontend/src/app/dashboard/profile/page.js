import { getMe } from '@/lib/api';
import { ProfileForm } from '@/components/dashboard/ProfileForm';

export default async function ProfilePage() {
  const { data: user } = await getMe();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>👤 پروفایل من</h1>
      <ProfileForm user={user} />
    </div>
  );
}