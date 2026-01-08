import { useState } from 'react';
import { User, Bot, ChevronDown, ChevronUp, Copy, Download, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { Message } from '@/types';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [showCode, setShowCode] = useState(false);
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopyCode = () => {
    if (message.code) {
      navigator.clipboard.writeText(message.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={cn("message-fade-in py-4", isUser ? "bg-transparent" : "bg-surface/50")}>
      <div className="max-w-3xl mx-auto px-4">
        <div className="flex gap-4">
          {/* Avatar */}
          <div className={cn(
            "w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center",
            isUser ? "bg-secondary" : "bg-primary"
          )}>
            {isUser ? (
              <User className="w-4 h-4" />
            ) : (
              <Bot className="w-4 h-4 text-primary-foreground" />
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-3">
            <p className="text-sm font-medium">
              {isUser ? 'You' : 'Assistant'}
            </p>
            
            <p className="text-foreground">{message.content}</p>

            {/* Code Section */}
            {message.code && (
              <div className="rounded-lg border border-border overflow-hidden">
                <button
                  onClick={() => setShowCode(!showCode)}
                  className="w-full flex items-center justify-between px-4 py-2.5 bg-surface hover:bg-surface-hover transition-colors"
                >
                  <span className="text-sm font-medium flex items-center gap-2">
                    💻 Code
                  </span>
                  {showCode ? (
                    <ChevronUp className="w-4 h-4 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                  )}
                </button>
                
                {showCode && (
                  <div className="relative">
                    <pre className="p-4 bg-muted/50 overflow-x-auto text-sm font-mono">
                      <code>{message.code}</code>
                    </pre>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleCopyCode}
                      className="absolute top-2 right-2 h-8 gap-1.5"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3.5 h-3.5" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* Visualization */}
            {message.outputType === 'visualization' && message.chartUrl && (
              <div className="space-y-3">
                <p className="text-sm font-medium flex items-center gap-2">
                  🎨 Visualization
                </p>
                <div className="rounded-lg border border-border overflow-hidden bg-card">
                  <img 
                    src={message.chartUrl} 
                    alt="Data visualization" 
                    className="w-full max-h-[400px] object-contain"
                  />
                </div>
                <Button variant="outline" size="sm" className="gap-2">
                  <Download className="w-3.5 h-3.5" />
                  Download PNG
                </Button>
              </div>
            )}

            {/* Modification */}
            {message.outputType === 'modification' && message.modifiedData && (
              <div className="space-y-3">
                <p className="text-sm font-medium flex items-center gap-2">
                  💾 Modified Data
                </p>
                
                <div className="flex gap-6 text-sm">
                  <div>
                    <span className="text-muted-foreground">Rows: </span>
                    <span className="font-medium">
                      {message.modifiedData.beforeRows.toLocaleString()} → {message.modifiedData.afterRows.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Columns: </span>
                    <span className="font-medium">
                      {message.modifiedData.beforeColumns} → {message.modifiedData.afterColumns}
                    </span>
                  </div>
                </div>

                <div className="rounded-lg border border-border overflow-hidden">
                  <div className="px-4 py-2 bg-surface border-b border-border">
                    <span className="text-sm font-medium">Preview (first {message.modifiedData.preview.length} rows)</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-muted/50">
                        <tr>
                          {Object.keys(message.modifiedData.preview[0] || {}).map((key) => (
                            <th key={key} className="px-4 py-2 text-left font-medium text-muted-foreground">
                              {key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {message.modifiedData.preview.map((row, i) => (
                          <tr key={i} className="border-t border-border">
                            {Object.values(row).map((value, j) => (
                              <td key={j} className="px-4 py-2">
                                {String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <Button variant="outline" size="sm" className="gap-2">
                  <Download className="w-3.5 h-3.5" />
                  Download CSV
                </Button>
              </div>
            )}

            {/* Exploratory Output */}
            {message.outputType === 'exploratory' && message.output && (
              <div className="space-y-2">
                <p className="text-sm font-medium flex items-center gap-2">
                  📊 Output
                </p>
                <div className="p-4 rounded-lg bg-muted/50 font-mono text-sm">
                  {message.output}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
