"use client";

import type { ChatMessage as ChatMessageType, Citation } from "@/lib/types";
import { Robot, User, Play } from "@phosphor-icons/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function CitationPill({ 
  cite, 
  index, 
  onClick 
}: { 
  cite: Citation; 
  index: number; 
  onClick: () => void; 
}) {
  return (
    <button
      onClick={onClick}
      className="group flex items-center overflow-hidden rounded-full bg-[var(--bg-glass-strong)] border border-[var(--border)] hover:border-[var(--accent)] active:scale-[0.97] transition-all duration-300 ease-[cubic-bezier(0.23,1,0.32,1)] focus:outline-none"
      style={{ height: "26px" }}
      title={`Skip to ${cite.start_time}s`}
    >
      <div className="flex h-full w-[26px] shrink-0 items-center justify-center text-[11px] font-medium text-[var(--text-secondary)] group-hover:bg-[var(--accent-muted)] group-hover:text-[var(--accent)] transition-colors duration-300">
        {index + 1}
      </div>
      <div className="max-w-0 overflow-hidden whitespace-nowrap text-[11px] font-mono text-[var(--text-secondary)] opacity-0 transition-all duration-300 ease-[cubic-bezier(0.23,1,0.32,1)] group-hover:max-w-[250px] group-hover:opacity-100 group-hover:px-2 group-hover:pr-3">
        <span className="flex items-center gap-1.5">
          <Play size={10} weight="fill" className="text-[var(--accent)]" />
          {(cite.text || cite.chunk_text || "").slice(0, 40)}...
        </span>
      </div>
    </button>
  );
}

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
  onCitationClick?: (videoId: string, startTime: string) => void;
  onVideoHighlightClick?: (videoId: string) => void;
  videoContexts?: Record<string, { label: string; durationSec: number }>;
}

export default function ChatMessage({
  message,
  isStreaming,
  onCitationClick,
  onVideoHighlightClick,
  videoContexts,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  const processedContent = isUser 
    ? message.content 
    : message.content.replace(
        /`?\[Video:\s*([^,\]]+),\s*([0-9.]+)s\s*-\s*([0-9.]+)s\]`?/g,
        (match, videoId, start, end) => {
          const v = videoContexts?.[videoId];
          // If the citation starts near the beginning and covers at least 85% of the video
          // (transcripts are often shorter than metadata duration due to outro music/silence)
          if (v && parseFloat(start) <= 5 && parseFloat(end) >= v.durationSec * 0.85) {
            return `[${v.label}](#video-highlight:${videoId})`;
          }
          return `[${start}s - ${end}s](#video-cite:${videoId}:${start})`;
        }
      ).replace(
        /`?\[Video:\s*([^,\]]+)\]`?/g,
        (match, videoId) => {
          const v = videoContexts?.[videoId];
          return `[${v ? v.label : "Video"}](#video-highlight:${videoId})`;
        }
      );

  return (
    <div id={`message-${message.id}`} className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      <div
        className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
        style={{
          background: isUser
            ? "var(--text-primary)"
            : "var(--bg-glass-strong)",
          color: isUser ? "var(--bg-app)" : "var(--text-secondary)",
          boxShadow: isUser ? "none" : "var(--neu-raised)",
          border: "1px solid var(--border)",
        }}
      >
        {isUser ? (
          <User size={15} weight="bold" className="text-current" />
        ) : (
          <Robot size={15} weight="bold" className="text-[var(--text-secondary)]" />
        )}
      </div>

      <div
        className="max-w-[78%] rounded-[var(--radius-xl)] px-4 py-3 text-[13px] leading-relaxed text-left"
        style={{
          background: isUser
            ? "var(--text-primary)"
            : "transparent",
          color: isUser ? "var(--bg-app)" : "var(--text-primary)",
          border: isUser ? "1px solid var(--border)" : "1px solid transparent",
          boxShadow: "none",
        }}
      >
        <div className="prose prose-sm prose-invert max-w-none text-current">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
              ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
              ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
              li: ({ node, ...props }) => <li className="" {...props} />,
              h1: ({ node, ...props }) => <h1 className="text-lg font-semibold mb-3 mt-5 first:mt-0" {...props} />,
              h2: ({ node, ...props }) => <h2 className="text-base font-semibold mb-3 mt-4 first:mt-0" {...props} />,
              h3: ({ node, ...props }) => <h3 className="text-sm font-semibold mb-2 mt-3 first:mt-0" {...props} />,
              a: ({ node, href, children, ...props }) => {
                if (href?.startsWith("#video-cite:")) {
                  const [, videoId, startTime] = href.split(":");
                  return (
                    <button
                      onClick={() => onCitationClick && onCitationClick(videoId, startTime)}
                      className="inline-flex items-center gap-1 cursor-pointer rounded-md bg-[var(--accent-muted)] px-1.5 py-0.5 text-[11px] font-mono text-[var(--accent)] hover:bg-[var(--accent)] hover:text-[var(--bg-app)] active:scale-[0.97] transition-all duration-200 focus:outline-none align-baseline"
                      title="Jump to video timestamp"
                    >
                      <Play size={10} weight="fill" />
                      {children}
                    </button>
                  );
                }
                if (href?.startsWith("#video-highlight:")) {
                  const [, videoId] = href.split(":");
                  return (
                    <button
                      onClick={() => onVideoHighlightClick && onVideoHighlightClick(videoId)}
                      className="inline-flex items-center gap-1 cursor-pointer rounded-md bg-[var(--bg-glass-strong)] border border-[var(--border)] px-1.5 py-0.5 text-[11px] font-mono text-[var(--text-secondary)] hover:border-[var(--accent)] hover:text-[var(--accent)] active:scale-[0.97] transition-all duration-200 focus:outline-none align-baseline"
                      title="Highlight video card"
                    >
                      <Play size={10} className="opacity-70" />
                      {children}
                    </button>
                  );
                }
                return (
                  <a
                    className="text-[var(--accent)] hover:underline underline-offset-2 transition-colors duration-200"
                    target="_blank"
                    rel="noopener noreferrer"
                    href={href}
                    {...props}
                  >
                    {children}
                  </a>
                );
              },
              strong: ({ node, ...props }) => <strong className="font-semibold" {...props} />,
              code: ({ node, ...props }) => (
                <code className="bg-[var(--bg-glass-strong)] px-1.5 py-0.5 rounded-md text-[0.9em] font-mono" {...props} />
              ),
              pre: ({ node, ...props }) => (
                <pre className="bg-[var(--bg-glass-strong)] p-3 rounded-lg overflow-x-auto mb-3 text-[0.9em] font-mono border border-[var(--border)] [&>code]:bg-transparent [&>code]:p-0" {...props} />
              ),
              blockquote: ({ node, ...props }) => (
                <blockquote className="border-l-2 border-[var(--accent)] pl-3 italic text-[var(--text-secondary)] my-3" {...props} />
              ),
              table: ({ node, ...props }) => (
                <div className="overflow-x-auto mb-3 border border-[var(--border)] rounded-lg">
                  <table className="min-w-full divide-y divide-[var(--border)]" {...props} />
                </div>
              ),
              thead: ({ node, ...props }) => <thead className="bg-[var(--bg-glass-strong)]" {...props} />,
              th: ({ node, ...props }) => (
                <th className="px-4 py-2 text-left text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider" {...props} />
              ),
              td: ({ node, ...props }) => <td className="px-4 py-2 text-sm border-t border-[var(--border)]" {...props} />,
            }}
          >
            {processedContent}
          </ReactMarkdown>
        </div>

        {isStreaming && (
          <span
            className="ml-0.5 inline-block h-4 w-1.5 animate-pulse rounded-sm align-middle"
            style={{ background: "var(--accent)" }}
          />
        )}

        {message.reasoning && (
          <details className="mt-3 group">
            <summary className="cursor-pointer text-[11px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors duration-200 ease-out select-none flex items-center gap-1.5">
              <span className="flex items-center justify-center w-4 h-4 rounded-full bg-[var(--bg-glass-strong)] border border-[var(--border)] group-open:bg-[var(--accent-muted)] group-open:text-[var(--accent)] transition-colors duration-200">
                <svg width="8" height="8" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg" className="transform transition-transform duration-200 group-open:rotate-90">
                  <path d="M3.5 1.5L7.5 5L3.5 8.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              Thought process
            </summary>
            <div className="mt-2 pl-3 border-l-[1.5px] border-[var(--border)] py-1 pr-2">
              <p className="whitespace-pre-wrap text-[12px] text-[var(--text-secondary)] font-mono leading-relaxed opacity-80">
                {message.reasoning}
              </p>
            </div>
          </details>
        )}

        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2 border-t border-[var(--border)] pt-3">
            {message.citations.map((cite: Citation, i: number) => (
              <CitationPill 
                key={i} 
                cite={cite} 
                index={i} 
                onClick={() => onCitationClick && onCitationClick(cite.video_id, cite.start_time)} 
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
