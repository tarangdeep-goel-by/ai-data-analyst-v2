import { useEffect, useState } from 'react';
import { Plus, MessageSquare, ExternalLink, Database, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function ProjectHome() {
  const {
    activeProjectId,
    getActiveProject,
    getProjectChats,
    setActiveChat,
    setShowDataModal,
    createChat,
    loadChats,
    deleteProject,
  } = useAppStore();

  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const project = getActiveProject();
  const chats = activeProjectId ? getProjectChats(activeProjectId) : [];

  // Load chats when project changes
  useEffect(() => {
    if (activeProjectId) {
      loadChats(activeProjectId);
    }
  }, [activeProjectId, loadChats]);

  if (!project) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <div className="w-16 h-16 rounded-2xl bg-surface mx-auto mb-6 flex items-center justify-center">
            <Database className="w-8 h-8 text-muted-foreground" />
          </div>
          <h2 className="text-2xl font-semibold mb-2">Select a Project</h2>
          <p className="text-muted-foreground">
            Choose a project from the sidebar or create a new one to start analyzing your data.
          </p>
        </div>
      </div>
    );
  }

  const handleNewChat = () => {
    if (activeProjectId) {
      createChat(activeProjectId);
    }
  };

  const handleDeleteProject = async () => {
    if (!activeProjectId) return;

    setIsDeleting(true);
    try {
      await deleteProject(activeProjectId);
      setShowDeleteDialog(false);
    } catch (error) {
      // Error is already handled in store with toast
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="flex-1 overflow-hidden">
      <div className="h-full overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Project Header */}
          <div className="mb-8 animate-fade-in">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Database className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h1 className="text-2xl font-semibold">{project.name}</h1>
                  <p className="text-muted-foreground">
                    {project.datasetFilename} • {project.rowCount.toLocaleString()} rows, {project.columnCount} columns
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2"
                  onClick={() => setShowDataModal(true)}
                >
                  View Data
                  <ExternalLink className="w-3.5 h-3.5" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="gap-2 text-destructive hover:text-destructive hover:bg-destructive/10"
                  onClick={() => setShowDeleteDialog(true)}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete
                </Button>
              </div>
            </div>
          </div>

          {/* Chats Section */}
          <div className="animate-fade-in" style={{ animationDelay: '100ms' }}>
            <h2 className="text-lg font-medium mb-4">Chats</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* New Chat Card */}
              <button
                onClick={handleNewChat}
                className={cn(
                  "group p-5 rounded-xl border-2 border-dashed border-border",
                  "hover:border-primary hover:bg-primary/5",
                  "transition-all duration-200 text-left"
                )}
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3 group-hover:bg-primary/20 transition-colors">
                  <Plus className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-medium mb-1">Start New Chat</h3>
                <p className="text-sm text-muted-foreground">
                  Begin analyzing your data
                </p>
              </button>

              {/* Existing Chats */}
              {chats.map((chat, index) => (
                <button
                  key={chat.id}
                  onClick={() => setActiveChat(chat.id)}
                  className={cn(
                    "card-hover p-5 rounded-xl bg-card border border-border",
                    "hover:border-primary/50 transition-all duration-200 text-left"
                  )}
                  style={{ animationDelay: `${(index + 1) * 50}ms` }}
                >
                  <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center mb-3">
                    <MessageSquare className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <h3 className="font-medium mb-1 truncate">{chat.name}</h3>
                  <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
                    "{chat.firstQuery}"
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {chat.messageCount} messages • {formatDistanceToNow(chat.lastActive, { addSuffix: true })}
                  </p>
                </button>
              ))}
            </div>

            {chats.length === 0 && (
              <p className="text-muted-foreground text-center py-8 mt-4">
                No chats yet. Start your first analysis!
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{project?.name}"? This will permanently remove the project,
              all chats, messages, and associated data. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteProject}
              disabled={isDeleting}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isDeleting ? 'Deleting...' : 'Delete Project'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
