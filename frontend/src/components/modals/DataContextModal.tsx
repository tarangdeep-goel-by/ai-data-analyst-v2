import { useState, useEffect } from 'react';
import { X, Download, Database } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/store/appStore';
import type { DatasetContext } from '@/types';

export function DataContextModal() {
  const { showDataModal, setShowDataModal, activeProjectId, getDatasetContext } = useAppStore();
  const [context, setContext] = useState<DatasetContext | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load dataset context when modal opens
  useEffect(() => {
    if (showDataModal && activeProjectId) {
      setIsLoading(true);
      getDatasetContext(activeProjectId)
        .then((ctx) => {
          setContext(ctx);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Failed to load dataset context:', error);
          setIsLoading(false);
        });
    }
  }, [showDataModal, activeProjectId, getDatasetContext]);

  if (!showDataModal) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={() => setShowDataModal(false)}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-3xl max-h-[85vh] bg-card border border-border rounded-2xl shadow-lg overflow-hidden animate-fade-in mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Database className="w-5 h-5 text-primary" />
            </div>
            <h2 className="text-lg font-semibold">Dataset Context</h2>
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setShowDataModal(false)}
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(85vh-140px)]">
          <div className="p-6 space-y-6">
            {isLoading ? (
              <div className="flex items-center justify-center py-12">
                <p className="text-muted-foreground">Loading dataset context...</p>
              </div>
            ) : !context ? (
              <div className="flex items-center justify-center py-12">
                <p className="text-muted-foreground">No dataset context available</p>
              </div>
            ) : (
              <>
                {/* Overview */}
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
                    📊 Dataset Overview
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg bg-surface">
                      <p className="text-sm text-muted-foreground">File</p>
                      <p className="font-medium">{context.filename}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-surface">
                      <p className="text-sm text-muted-foreground">Size</p>
                      <p className="font-medium">
                        {context.rowCount.toLocaleString()} rows × {context.columnCount} columns
                      </p>
                    </div>
                  </div>
                </div>

            {/* Columns */}
            <div>
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
                📋 Columns
              </h3>
              <div className="rounded-lg border border-border overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">Column Name</th>
                      <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">Type</th>
                      <th className="px-4 py-2.5 text-right font-medium text-muted-foreground">Nulls</th>
                    </tr>
                  </thead>
                  <tbody>
                    {context.columns.map((col, i) => (
                      <tr key={i} className="border-t border-border">
                        <td className="px-4 py-2.5 font-mono text-sm">{col.name}</td>
                        <td className="px-4 py-2.5 text-muted-foreground">{col.type}</td>
                        <td className="px-4 py-2.5 text-right">{col.nullPercentage.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Sample Data */}
            <div>
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
                📈 Sample Data (first {context.sampleData.length} rows)
              </h3>
              <div className="rounded-lg border border-border overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      {Object.keys(context.sampleData[0] || {}).map((key) => (
                        <th key={key} className="px-4 py-2.5 text-left font-medium text-muted-foreground whitespace-nowrap">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {context.sampleData.map((row, i) => (
                      <tr key={i} className="border-t border-border">
                        {Object.values(row).map((value, j) => (
                          <td key={j} className="px-4 py-2.5 whitespace-nowrap">
                            {String(value)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

                {/* Statistics */}
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide mb-3">
                    📝 Statistics
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg bg-surface text-center">
                      <p className="text-2xl font-semibold">{context.numericColumns}</p>
                      <p className="text-sm text-muted-foreground">Numeric columns</p>
                    </div>
                    <div className="p-4 rounded-lg bg-surface text-center">
                      <p className="text-2xl font-semibold">{context.categoricalColumns}</p>
                      <p className="text-sm text-muted-foreground">Categorical columns</p>
                    </div>
                    <div className="p-4 rounded-lg bg-surface text-center">
                      <p className="text-2xl font-semibold">{context.missingValuePercentage.toFixed(1)}%</p>
                      <p className="text-sm text-muted-foreground">Missing values</p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border bg-card">
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" />
            Download Full Dataset
          </Button>
        </div>
      </div>
    </div>
  );
}
