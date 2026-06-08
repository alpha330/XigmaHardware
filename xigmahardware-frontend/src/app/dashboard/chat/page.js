import { getActiveChats } from '@/lib/api';
import { ChatPanel } from '@/components/dashboard/ChatPanel';

export default async function ChatPage() {
  const { data } = await getActiveChats();

  return (
    <div className="animate-fade-in-up">
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: 24 }}>💬 چت‌های فعال</h1>
      <ChatPanel chats={data?.results || []} />
    </div>
  );
}