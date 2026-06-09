import clsx from "clsx";
import { useState } from "react";
import { ArrowsClockwise, Trash, ArrowRight, Link } from "@phosphor-icons/react";

interface IngestModalProps {
  isOpen: boolean;
  results: { url: string; status: string; message?: string }[];
  onProceed: () => void;
  onRetry: () => void;
  onReplace: (failedUrl: string, newUrl: string) => void;
  onCancel: () => void;
}

export default function IngestModal({
  isOpen,
  results,
  onProceed,
  onRetry,
  onReplace,
  onCancel,
}: IngestModalProps) {
  const [showReplaceInput, setShowReplaceInput] = useState<string | null>(null);
  const [newUrl, setNewUrl] = useState("");

  if (!isOpen) return null;

  const failedVideos = results.filter((r) => r.status === "error");
  const successfulVideos = results.filter((r) => r.status !== "error");

  const handleReplaceSubmit = (e: React.FormEvent, failedUrl: string) => {
    e.preventDefault();
    if (newUrl.trim()) {
      onReplace(failedUrl, newUrl.trim());
      setShowReplaceInput(null);
      setNewUrl("");
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-[var(--radius-2xl)] bg-[var(--bg-surface)] p-6 border border-[var(--border)] shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
          Ingestion Issue
        </h3>
        <p className="text-sm text-[var(--text-secondary)] mb-6">
          There was an issue fetching transcripts for some of the videos.
        </p>

        <div className="space-y-4 mb-8">
          {results.map((result, idx) => (
            <div
              key={idx}
              className={clsx(
                "p-4 rounded-[var(--radius-lg)] border",
                result.status === "error"
                  ? "bg-red-500/5 border-red-500/20"
                  : "bg-green-500/5 border-green-500/20"
              )}
            >
              <div className="flex items-start justify-between">
                <div className="min-w-0 pr-4">
                  <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                    {result.url}
                  </p>
                  <p
                    className={clsx(
                      "text-xs mt-1",
                      result.status === "error"
                        ? "text-red-500"
                        : "text-green-500"
                    )}
                  >
                    {result.status === "error"
                      ? result.message || "Failed to fetch transcript"
                      : "Successfully fetched"}
                  </p>
                </div>
              </div>

              {result.status === "error" && (
                <div className="mt-4 pt-4 border-t border-red-500/10 flex flex-col gap-2">
                  {showReplaceInput === result.url ? (
                    <form
                      onSubmit={(e) => handleReplaceSubmit(e, result.url)}
                      className="flex items-center gap-2"
                    >
                      <input
                        type="url"
                        placeholder="Paste new YouTube URL..."
                        value={newUrl}
                        onChange={(e) => setNewUrl(e.target.value)}
                        className="flex-1 bg-[var(--bg-surface-hover)] border border-[var(--border-subtle)] rounded-[var(--radius-md)] px-3 py-1.5 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--border)]"
                        autoFocus
                      />
                      <button
                        type="submit"
                        disabled={!newUrl.trim()}
                        className="px-3 py-1.5 rounded-[var(--radius-md)] bg-[var(--text-primary)] text-[var(--bg-surface)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
                      >
                        Go
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowReplaceInput(null)}
                        className="px-3 py-1.5 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                      >
                        Cancel
                      </button>
                    </form>
                  ) : (
                    <div className="flex items-center gap-3">
                      <button
                        onClick={onRetry}
                        className="flex items-center gap-1.5 text-xs font-medium text-red-500 hover:text-red-400 bg-red-500/10 hover:bg-red-500/20 px-3 py-1.5 rounded-[var(--radius-sm)] transition-colors"
                      >
                        <ArrowsClockwise size={14} />
                        Retry
                      </button>
                      <button
                        onClick={() => setShowReplaceInput(result.url)}
                        className="flex items-center gap-1.5 text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] bg-[var(--bg-surface-hover)] hover:bg-[var(--border-subtle)] px-3 py-1.5 rounded-[var(--radius-sm)] transition-colors"
                      >
                        <Link size={14} />
                        Replace Video
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center pt-2 border-t border-[var(--border)]">
          <button
            onClick={onCancel}
            className="flex items-center gap-2 px-4 py-2 rounded-[var(--radius-md)] text-sm font-medium text-red-500 hover:bg-red-500/10 transition-colors"
          >
            <Trash size={16} />
            Delete Session
          </button>
          
          <button
            onClick={onProceed}
            disabled={successfulVideos.length === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-[var(--radius-md)] text-sm font-medium bg-[var(--text-primary)] text-[var(--bg-surface)] hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Proceed Anyway
            <ArrowRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
