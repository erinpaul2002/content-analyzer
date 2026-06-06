"use client";

import { useState, useRef, useEffect } from "react";
import { ArrowUp, Equalizer, CircleNotch, CaretUp, CaretDown } from "@phosphor-icons/react";
import clsx from "clsx";
import ChatMessage from "./ChatMessage";
import type { ChatMessage as ChatMessageType } from "@/lib/types";

interface ChatPanelProps {
  messages: ChatMessageType[];
  onSend: (message: string) => void;
  isStreaming: boolean;
  appState: "idle" | "loading" | "ready";
  canCompare: boolean;
  onCompare: () => void;
  onCitationClick?: (videoId: string, startTime: string) => void;
  onVideoHighlightClick?: (videoId: string) => void;
  videoContexts?: Record<string, { label: string; durationSec: number }>;
}

function ScrollNavigator({ 
  messages, 
  scrollRef 
}: { 
  messages: ChatMessageType[]; 
  scrollRef: React.RefObject<HTMLDivElement | null>;
}) {
  const [visibleMessageId, setVisibleMessageId] = useState<string | null>(null);
  const [hoverInfo, setHoverInfo] = useState<{ top: number; text: string; role: string } | null>(null);
  const navigatorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;

    let timeoutId: NodeJS.Timeout;

    const handleScroll = () => {
      if (!scrollRef.current) return;
      const containerRect = scrollRef.current.getBoundingClientRect();
      let closestMsgId = null;
      let minDistance = Infinity;

      messages.forEach((msg) => {
        const el = document.getElementById(`message-${msg.id}`);
        if (el) {
          const rect = el.getBoundingClientRect();
          const distance = Math.abs(rect.top - containerRect.top);
          if (distance < minDistance) {
            minDistance = distance;
            closestMsgId = msg.id;
          }
        }
      });

      if (closestMsgId) {
        setVisibleMessageId(closestMsgId);
      }
    };

    const throttledScroll = () => {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(handleScroll, 50);
    };

    container.addEventListener('scroll', throttledScroll);
    handleScroll();

    return () => {
      container.removeEventListener('scroll', throttledScroll);
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [messages, scrollRef]);

  if (messages.length < 2) return null;

  const handleScrollTo = (id: string) => {
    const el = document.getElementById(`message-${id}`);
    if (el && scrollRef.current) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setVisibleMessageId(id);
    }
  };

  const activeId = visibleMessageId || messages[messages.length - 1]?.id;
  const activeIndex = messages.findIndex(m => m.id === activeId);

  const handlePrev = () => {
    if (activeIndex > 0) {
      handleScrollTo(messages[activeIndex - 1].id);
    }
  };

  const handleNext = () => {
    if (activeIndex < messages.length - 1 && activeIndex !== -1) {
      handleScrollTo(messages[activeIndex + 1].id);
    }
  };

  const handleMouseEnter = (e: React.MouseEvent, msg: ChatMessageType) => {
    if (!navigatorRef.current) return;
    const navRect = navigatorRef.current.getBoundingClientRect();
    const btnRect = e.currentTarget.getBoundingClientRect();
    
    setHoverInfo({
      top: btnRect.top - navRect.top + btnRect.height / 2,
      text: msg.content.substring(0, 120).replace(/\s+/g, ' '),
      role: msg.role
    });
  };

  const handleMouseLeave = () => {
    setHoverInfo(null);
  };

  return (
    <div ref={navigatorRef} className="absolute right-2 top-2 bottom-2 flex flex-col items-center py-1 z-10 w-6">
      <button onClick={handlePrev} disabled={activeIndex <= 0} className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors p-1 cursor-pointer shrink-0">
        <CaretUp size={14} weight="bold" />
      </button>
      
      <div className="flex flex-col items-center justify-center flex-1 min-h-0 w-full overflow-y-auto hide-scrollbar">
        <div className="flex flex-col items-center justify-center gap-1.5 w-full h-max py-2">
          {messages.map((msg) => {
            const isActive = msg.id === activeId;
            let widthClass = "";
            let bgClass = "";

            if (isActive) {
              widthClass = "w-6";
              bgClass = "bg-[var(--text-primary)]";
            } else {
              bgClass = "bg-[var(--text-tertiary)] hover:bg-[var(--text-secondary)]";
              if (msg.role === "user") {
                widthClass = "w-2 hover:w-3";
              } else {
                widthClass = "w-4 hover:w-5";
              }
            }

            return (
              <div 
                key={msg.id}
                className="w-full flex justify-center py-0.5"
                onMouseEnter={(e) => handleMouseEnter(e, msg)}
                onMouseLeave={handleMouseLeave}
              >
                <button
                  onClick={() => handleScrollTo(msg.id)}
                  className={clsx(
                    "h-1 rounded-full transition-all duration-300 cursor-pointer shrink-0",
                    widthClass,
                    bgClass
                  )}
                  aria-label="Scroll to message"
                />
              </div>
            );
          })}
        </div>
      </div>

      <button onClick={handleNext} disabled={activeIndex >= messages.length - 1} className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors p-1 cursor-pointer shrink-0">
        <CaretDown size={14} weight="bold" />
      </button>

      {/* Tooltip Preview */}
      {hoverInfo && (
        <div 
          className="absolute right-full mr-3 -translate-y-1/2 pointer-events-none z-50 transition-all duration-200 ease-out"
          style={{ top: hoverInfo.top }}
        >
          <div className="flex items-center bg-[var(--bg-glass-strong)] backdrop-blur-2xl border border-[var(--border-strong)] rounded-full px-4 py-1.5 text-[12px] shadow-xl max-w-[280px] shadow-black/20 overflow-hidden">
            <span className="font-semibold text-[var(--text-secondary)] mr-2 shrink-0">
              {hoverInfo.role === 'user' ? 'You:' : 'AI:'}
            </span>
            <span className="text-[var(--text-primary)] whitespace-nowrap overflow-hidden text-ellipsis">
              {hoverInfo.text}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ChatPanel({
  messages,
  onSend,
  isStreaming,
  appState,
  canCompare,
  onCompare,
  onCitationClick,
  onVideoHighlightClick,
  videoContexts,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  function handleSubmit(e?: React.FormEvent) {
    e?.preventDefault();
    if (appState !== "ready") {
      if (canCompare && appState === "idle") {
        onCompare();
      }
      return;
    }
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setInput("");
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  const isReady = appState === "ready";
  const canSend = Boolean(input.trim()) && !isStreaming && isReady;

  return (
    <div className="flex flex-col h-full">
      {messages.length > 0 && (
        <div className="relative mb-3 flex-1 min-h-0">
          <div
            ref={scrollRef}
            className="h-full space-y-4 overflow-y-auto rounded-[var(--radius-2xl)] glass-panel px-4 py-4 hide-scrollbar pr-10"
          >
            {messages.map((msg, i) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              isStreaming={
                isStreaming && i === messages.length - 1 && msg.role === "assistant"
              }
              onCitationClick={onCitationClick}
              onVideoHighlightClick={onVideoHighlightClick}
              videoContexts={videoContexts}
            />
          ))}
          </div>
          <ScrollNavigator messages={messages} scrollRef={scrollRef} />
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex w-full flex-col items-center">
        <div
          className={clsx(
            "relative flex h-14 items-center overflow-hidden transition-all duration-500 ease-[var(--ease-in-out)]",
            "rounded-[var(--radius-2xl)]",
            "bg-[var(--bg-surface)] backdrop-blur-2xl border border-[var(--border-strong)]",
            "ring-1 ring-black/5 dark:ring-white/5",
            (appState === "idle" || appState === "loading")
              ? "w-[240px] max-w-full"
              : "w-full focus-within:border-[var(--text-secondary)] focus-within:-translate-y-0.5",
            canCompare && appState === "idle" && "hover:border-[var(--text-secondary)] hover:-translate-y-0.5"
          )}
        >
          {/* Button Overlay for Idle/Loading */}
          <button
            type="button"
            onClick={onCompare}
            disabled={!canCompare || appState === "loading"}
            className={clsx(
              "absolute inset-0 flex w-full items-center justify-center gap-3 px-4 font-semibold transition-all duration-500",
              (appState === "idle" || appState === "loading")
                ? clsx(
                    "z-10 opacity-100",
                    (!canCompare || appState === "loading") 
                      ? "cursor-not-allowed opacity-50 text-[var(--text-tertiary)]"
                      : "cursor-pointer text-[var(--text-primary)] hover:bg-[var(--bg-surface-hover)]"
                  )
                : "-z-10 scale-95 opacity-0 pointer-events-none"
            )}
          >
            {appState === "loading" ? (
              <>
                <CircleNotch size={20} className="animate-spin text-[var(--text-secondary)]" />
                <span className="whitespace-nowrap">Analyzing...</span>
              </>
            ) : (
              <>
                <Equalizer size={20} weight="bold" />
                <span className="whitespace-nowrap">Compare Videos</span>
              </>
            )}
          </button>

          {/* Chat Input Overlay for Ready */}
          <div
            className={clsx(
              "absolute inset-0 flex w-full items-center gap-3 px-4 transition-all duration-500",
              appState === "ready"
                ? "z-10 opacity-100 delay-150"
                : "-z-10 scale-105 opacity-0 pointer-events-none"
            )}
          >
            <input
              ref={inputRef}
              id="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question"
              className="min-w-0 flex-1 bg-transparent text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-tertiary)]"
            />
            <button
              type="submit"
              disabled={!canSend}
              className={clsx(
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-[var(--radius-md)] press-scale cursor-pointer",
                "disabled:cursor-not-allowed disabled:opacity-70",
                canSend 
                  ? "border-[1.5px] border-[var(--bg-app)]" 
                  : "border-[1.5px] border-[var(--text-tertiary)]"
              )}
              style={{
                background: canSend ? "var(--text-primary)" : "var(--bg-glass)",
                color: canSend ? "var(--bg-app)" : "var(--text-tertiary)",
                boxShadow: canSend ? "none" : "var(--neu-raised)",
                transitionDuration: "160ms",
                transitionTimingFunction: "var(--ease-out)",
              }}
              aria-label="Send message"
            >
              <ArrowUp size={17} weight="bold" className="text-current" />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
