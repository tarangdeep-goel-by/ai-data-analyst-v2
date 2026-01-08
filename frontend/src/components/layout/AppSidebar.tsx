import { useEffect, useState } from 'react';
import { Plus, Database, Settings, HelpCircle, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';
import { UploadProjectModal } from '@/components/modals/UploadProjectModal';

export function AppSidebar() {
  const {
    projects,
    activeProjectId,
    setActiveProject,
    loadProjects,
  } = useAppStore();

  const [showUploadModal, setShowUploadModal] = useState(false);

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleNewProject = () => {
    setShowUploadModal(true);
  };

  return (
    <aside className="glass-sidebar w-[280px] flex-shrink-0 flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="font-semibold text-lg">AI Data Analyst</h1>
        </div>
        
        <Button 
          onClick={handleNewProject}
          className="w-full gap-2"
          size="sm"
        >
          <Plus className="w-4 h-4" />
          New Project
        </Button>
      </div>

      {/* Projects List */}
      <ScrollArea className="flex-1 px-2 py-3">
        <div className="space-y-1">
          {projects.map((project) => (
            <button
              key={project.id}
              onClick={() => setActiveProject(project.id)}
              className={cn(
                "w-full p-3 rounded-lg text-left transition-all duration-150",
                "hover:bg-surface-hover",
                activeProjectId === project.id 
                  ? "bg-surface shadow-card" 
                  : "bg-transparent"
              )}
            >
              <div className="flex items-start gap-2">
                <Database className="w-4 h-4 mt-0.5 text-primary flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-sm truncate">
                    {project.name}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {project.datasetFilename} • {project.rowCount.toLocaleString()} rows
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatDistanceToNow(project.lastActive, { addSuffix: true })}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {projects.length === 0 && (
          <div className="text-center py-8 px-4">
            <Database className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
            <p className="text-sm text-muted-foreground">
              No projects yet. Create your first project to get started.
            </p>
          </div>
        )}
      </ScrollArea>

      {/* Footer */}
      <div className="p-3 border-t border-border flex items-center justify-between">
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <Settings className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <HelpCircle className="w-4 h-4" />
        </Button>
      </div>

      {/* Upload Project Modal */}
      <UploadProjectModal open={showUploadModal} onOpenChange={setShowUploadModal} />
    </aside>
  );
}
