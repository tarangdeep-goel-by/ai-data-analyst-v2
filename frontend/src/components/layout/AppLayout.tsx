import { AppSidebar } from './AppSidebar';
import { ProjectHome } from '@/components/project/ProjectHome';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { DataContextModal } from '@/components/modals/DataContextModal';
import { useAppStore } from '@/store/appStore';

export function AppLayout() {
  const { activeChatId } = useAppStore();

  return (
    <div className="flex h-screen w-full bg-background">
      <AppSidebar />
      
      <main className="flex-1 overflow-hidden">
        {activeChatId ? <ChatInterface /> : <ProjectHome />}
      </main>

      <DataContextModal />
    </div>
  );
}
