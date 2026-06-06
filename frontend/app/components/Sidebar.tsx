"use client";

import { useState } from "react";
import {
  CaretLeft,
  ChartBarHorizontal,
  ChatCircle,
  GearSix,
  Moon,
  Plus,
  Sun,
  Trash,
} from "@phosphor-icons/react";
import clsx from "clsx";
import type { SessionEntry } from "@/lib/types";
import ConfirmModal from "./ConfirmModal";


interface SidebarProps {
  activeSessionId?: string;
  sessions?: any[];
  onNewChat: () => void;
  onSelectSession?: (id: string) => void;
  onDeleteSession?: (id: string) => void;
  isDark: boolean;
  toggleTheme: () => void;
  collapsed: boolean;
  setCollapsed: (val: boolean) => void;
}

export default function Sidebar({
  activeSessionId,
  sessions = [],
  onNewChat,
  onSelectSession,
  onDeleteSession,
  isDark,
  toggleTheme,
  collapsed,
  setCollapsed,
}: SidebarProps) {
  const [sessionToDelete, setSessionToDelete] = useState<{id: string, title: string} | null>(null);

  // Group the dynamic sessions
  const groupedSessions = [
    {
      group: "Recent",
      items: sessions.map((s) => ({
        id: s.id,
        title: s.title,
        date: s.date,
      })),
    },
  ];

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-surface)] text-[var(--text-secondary)] press-scale cursor-pointer"
        style={{ transitionDuration: "120ms", boxShadow: "var(--shadow-soft)" }}
        aria-label="Open sidebar"
      >
        <ChartBarHorizontal size={18} />
      </button>
    );
  }

  return (
    <>
      <div
        className="fixed inset-0 z-30 bg-black/35 lg:hidden"
        style={{ backdropFilter: "blur(8px)" }}
        onClick={() => setCollapsed(true)}
      />

      <aside
        className="fixed bottom-0 left-0 top-0 z-40 flex w-[280px] flex-col overflow-hidden"
        style={{
          background: "var(--bg-sidebar)",
          backdropFilter: "blur(18px) saturate(140%)",
          WebkitBackdropFilter: "blur(18px) saturate(140%)",
          borderRight: "1px solid var(--border)",
          boxShadow: "var(--shadow-soft)",
        }}
      >
        <div className="px-4 pb-3 pt-5">
          <div className="flex items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
            <div className="flex min-w-0 items-center gap-3">
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[var(--radius-md)] text-[var(--text-primary)] neu-input"
                style={{
                  background: "var(--bg-input)",
                }}
              >
                <ChartBarHorizontal size={20} weight="bold" />
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold tracking-tight text-[var(--text-primary)]">
                  Analyzer
                </p>
              </div>
            </div>
            <button
              onClick={() => setCollapsed(true)}
              className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] press-scale cursor-pointer hover:bg-[var(--bg-surface-hover)]"
              style={{ transitionDuration: "120ms" }}
              aria-label="Collapse sidebar"
            >
              <CaretLeft size={16} className="text-[var(--text-secondary)]" />
            </button>
          </div>
        </div>

        <div className="px-4 pb-4">
          <button
            id="new-chat-btn"
            onClick={onNewChat}
            className="relative flex min-h-11 w-full items-center justify-center gap-2 overflow-hidden rounded-[var(--radius-md)] text-sm font-semibold press-scale cursor-pointer"
            style={{
              background: "var(--text-primary)",
              color: "var(--bg-app)",
              transitionDuration: "160ms",
              transitionTimingFunction: "var(--ease-out)",
            }}
          >
            <Plus size={17} weight="bold" />
            New Chat
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 pb-3 mt-2">
          {groupedSessions.map((group) => (
            <div key={group.group} className="mb-5">
              <p className="px-3 pb-2 text-[11px] font-medium uppercase tracking-[0.18em] text-[var(--text-tertiary)]">
                {group.group}
              </p>
              <ul className="overflow-hidden rounded-[var(--radius-md)]">
                {group.items.length === 0 && (
                  <li className="px-3 py-2 text-[12px] text-[var(--text-tertiary)] italic">No recent sessions</li>
                )}
                {group.items.map((entry) => (
                  <li key={entry.id}>
                    <div
                      role="button"
                      tabIndex={0}
                      onClick={() => onSelectSession?.(entry.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          onSelectSession?.(entry.id);
                        }
                      }}
                      className={clsx(
                        "w-full border-t border-[var(--border-subtle)] px-3 py-3 text-left press-scale first:border-t-0 cursor-pointer",
                        activeSessionId === entry.id
                          ? "bg-[var(--bg-surface-hover)]"
                          : "hover:bg-[var(--bg-surface-hover)]"
                      )}
                      style={{
                        transitionDuration: "140ms",
                      }}
                    >
                      <div className="flex items-start gap-3">
                        <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-[var(--radius-sm)] border border-[var(--border)]">
                          <ChatCircle size={16} className="text-[var(--text-secondary)]" />
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-[13px] font-medium text-[var(--text-primary)]">
                            {entry.title}
                          </p>
                          <div className="mt-1 flex items-center justify-between gap-2">
                            <span className="shrink-0 text-[11px] text-[var(--text-tertiary)]">
                              {entry.date}
                            </span>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setSessionToDelete({ id: entry.id, title: entry.title });
                              }}
                              className="text-[var(--text-tertiary)] hover:text-red-500 transition-colors"
                              aria-label="Delete session"
                            >
                              <Trash size={14} />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className="px-4 py-4">
          <div className="hairline mb-4" />
          <div className="flex items-center justify-between gap-3">
            <button
              className="flex min-h-10 flex-1 items-center gap-2.5 rounded-[var(--radius-md)] px-3 text-[13px] font-medium text-[var(--text-secondary)] press-scale cursor-pointer hover:bg-[var(--bg-surface-hover)] hover:text-[var(--text-primary)]"
              style={{ transitionDuration: "120ms" }}
            >
              <GearSix size={18} />
              Settings
            </button>
            <button
              onClick={toggleTheme}
              className="flex h-10 w-10 items-center justify-center rounded-[var(--radius-md)] press-scale cursor-pointer hover:bg-[var(--bg-surface-hover)]"
              style={{ transitionDuration: "120ms" }}
              aria-label="Toggle theme"
            >
              {isDark ? (
                <Sun size={16} className="text-[var(--text-secondary)]" />
              ) : (
                <Moon size={16} className="text-[var(--text-secondary)]" />
              )}
            </button>
          </div>
        </div>
      </aside>

      <ConfirmModal
        isOpen={sessionToDelete !== null}
        title="Delete Session"
        message={`Are you sure you want to delete "${sessionToDelete?.title}"? This action cannot be undone.`}
        onConfirm={() => {
          if (sessionToDelete) {
            onDeleteSession?.(sessionToDelete.id);
          }
          setSessionToDelete(null);
        }}
        onCancel={() => setSessionToDelete(null)}
      />
    </>
  );
}
