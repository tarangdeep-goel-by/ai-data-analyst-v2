import { useEffect, useRef } from 'react';
import { ArrowLeft, ExternalLink, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/sonner';
import { useAppStore } from '@/store/appStore';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

export function ChatInterface() {
  const {
    activeChatId,
    activeProjectId,
    getActiveProject,
    getActiveChat,
    getChatMessages,
    setActiveChat,
    setShowDataModal,
    addMessage,
    sendQuery,
    isLoading,
    setLoading,
  } = useAppStore();

  const project = getActiveProject();
  const chat = getActiveChat();
  const messages = activeChatId ? getChatMessages(activeChatId) : [];
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!activeChatId || !activeProjectId) {
      console.error('No active chat or project');
      return;
    }

    // Add user message optimistically
    addMessage({
      chatId: activeChatId,
      role: 'user',
      content,
    });

    // Send query to AI via API
    try {
      setLoading(true);
      await sendQuery(activeProjectId, activeChatId, content);
      // Messages are automatically reloaded by sendQuery
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message', {
        description: error instanceof Error ? error.message : 'An unexpected error occurred. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 h-14 border-b border-border flex items-center justify-between px-4 bg-background">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setActiveChat(null)}
            className="gap-1.5"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          <div className="h-5 w-px bg-border" />
          <span className="font-medium">{project?.name}</span>
          {chat && (
            <>
              <span className="text-muted-foreground">/</span>
              <span className="text-muted-foreground">{chat.name}</span>
            </>
          )}
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          className="gap-2"
          onClick={() => setShowDataModal(true)}
        >
          View Data
          <ExternalLink className="w-3.5 h-3.5" />
        </Button>
      </header>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md px-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 mx-auto mb-6 flex items-center justify-center">
                <Bot className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-xl font-semibold mb-2">Start a conversation</h2>
              <p className="text-muted-foreground">
                Ask questions about your data. I can help you explore, visualize, and transform your dataset.
              </p>
            </div>
          </div>
        ) : (
          <div className="pb-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {isLoading && (
              <div className="py-4 bg-surface/50">
                <div className="max-w-3xl mx-auto px-4">
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-lg bg-primary flex-shrink-0 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-primary-foreground" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium mb-2">Assistant</p>
                      <p className="text-muted-foreground">
                        Thinking<span className="thinking-dots" />
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}
