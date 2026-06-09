"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { Moon, Sun, SidebarSimple, ArrowsInSimple } from "@phosphor-icons/react";
import clsx from "clsx";
import Sidebar from "./components/Sidebar";
import VideoCard from "./components/VideoCard";
import { ComparisonSkeleton } from "./components/SkeletonLoader";
import ChatPanel from "./components/ChatPanel";
import IngestModal from "./components/IngestModal";
import { ingestVideos, streamMessage, getSessions, getSessionDetails, normalizeVideoPayload, deleteSession, confirmIngest } from "@/lib/api";
import { parseTimeToSeconds } from "@/lib/utils";
import type { ChatMessage, TranscriptSegment, VideoMetadata } from "@/lib/types";

type AppState = "idle" | "loading" | "ready";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<any[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Fetch sessions on initial load
  useEffect(() => {
    getSessions().then(setSessions).catch(console.error);
  }, []);
  const [isStreaming, setIsStreaming] = useState(false);
  const [urlA, setUrlA] = useState("");
  const [urlB, setUrlB] = useState("");
  const [videoA, setVideoA] = useState<VideoMetadata | undefined>();
  const [videoB, setVideoB] = useState<VideoMetadata | undefined>();
  const [transcriptA, setTranscriptA] = useState<TranscriptSegment[] | undefined>();
  const [transcriptB, setTranscriptB] = useState<TranscriptSegment[] | undefined>();
  const [isDark, setIsDark] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  const [isChatMinimized, setIsChatMinimized] = useState(false);
  const [seekRequestA, setSeekRequestA] = useState<{ time: number; t: number } | null>(null);
  const [seekRequestB, setSeekRequestB] = useState<{ time: number; t: number } | null>(null);
  const [highlightedVideoId, setHighlightedVideoId] = useState<string | null>(null);

  const [ingestResults, setIngestResults] = useState<{url: string, status: string, message?: string}[]>([]);
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [pendingSessionId, setPendingSessionId] = useState<string | null>(null);
  const [pendingVideos, setPendingVideos] = useState<any>(null);

  const videoContexts = useMemo(() => {
    const ctx: Record<string, { label: string; durationSec: number }> = {};
    if (videoA?.video_id) {
      ctx[videoA.video_id] = { label: "Video A", durationSec: parseTimeToSeconds(videoA.duration || "0") };
    }
    if (videoB?.video_id) {
      ctx[videoB.video_id] = { label: "Video B", durationSec: parseTimeToSeconds(videoB.duration || "0") };
    }
    return ctx;
  }, [videoA, videoB]);

  function toggleTheme() {
    const next = !isDark;
    setIsDark(next);
    document.documentElement.classList.toggle("dark", next);
  }

  const handleCitationClick = useCallback((videoId: string, startTime: string) => {
    const seconds = parseTimeToSeconds(startTime);
    if (videoA?.video_id === videoId) {
      setSeekRequestA({ time: seconds, t: Date.now() });
    } else if (videoB?.video_id === videoId) {
      setSeekRequestB({ time: seconds, t: Date.now() });
    }
  }, [videoA, videoB]);

  const handleVideoHighlightClick = useCallback((videoId: string) => {
    setHighlightedVideoId(videoId);
    // Clear highlight after 1.2s
    setTimeout(() => {
      setHighlightedVideoId((prev) => (prev === videoId ? null : prev));
    }, 1200);
  }, []);

  const handleCompare = useCallback(async (customUrlA?: string | React.MouseEvent, customUrlB?: string) => {
    const finalUrlA = typeof customUrlA === 'string' ? customUrlA : urlA;
    const finalUrlB = typeof customUrlB === 'string' ? customUrlB : urlB;

    if (!finalUrlA.trim() || !finalUrlB.trim()) return;

    setAppState("loading");
    setMessages([]);
    setVideoA(undefined);
    setVideoB(undefined);
    setTranscriptA(undefined);
    setTranscriptB(undefined);

    try {
      const res = await ingestVideos(finalUrlA.trim(), finalUrlB.trim());
      
      const hasErrors = res.results.some((r: any) => r.status === "error");
      
      if (hasErrors) {
        setIngestResults(res.results);
        setPendingSessionId(res.session_id);
        setPendingVideos(res.videos);
        setShowIngestModal(true);
        return;
      }
      
      await proceedToEmbedding(res.session_id, res.videos);
    } catch (err) {
      console.error("Ingest error:", err);
      setAppState("idle");
    }
  }, [urlA, urlB]);

  const proceedToEmbedding = useCallback(async (sid: string, videosObj: any) => {
    try {
      await confirmIngest(sid);
      setSessionId(sid);
      
      setVideoA(videosObj?.A?.metadata);
      setVideoB(videosObj?.B?.metadata);
      setTranscriptA(videosObj?.A?.transcript);
      setTranscriptB(videosObj?.B?.transcript);
      
      try {
        const updatedSessions = await getSessions();
        setSessions(updatedSessions);
      } catch (err) {
        console.error("Failed to refresh sessions:", err);
      }
      
      setAppState("ready");
    } catch (err) {
      console.error("Confirm ingest error:", err);
      setAppState("idle");
    }
  }, []);

  const handleProceedAnyway = () => {
    setShowIngestModal(false);
    if (pendingSessionId) {
      proceedToEmbedding(pendingSessionId, pendingVideos);
    }
  };

  const handleRetry = () => {
    setShowIngestModal(false);
    handleCompare(urlA, urlB);
  };

  const handleReplace = (failedUrl: string, newUrl: string) => {
    setShowIngestModal(false);
    if (failedUrl === urlA) {
      setUrlA(newUrl);
      handleCompare(newUrl, urlB);
    } else if (failedUrl === urlB) {
      setUrlB(newUrl);
      handleCompare(urlA, newUrl);
    }
  };

  const handleCancelIngest = async () => {
    setShowIngestModal(false);
    if (pendingSessionId) {
      try {
        await deleteSession(pendingSessionId);
      } catch (e) {
        console.error(e);
      }
    }
    handleNewChat();
  };

  const handleSend = useCallback(
    (message: string) => {
      if (!sessionId) return;

      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: message,
        timestamp: new Date(),
      };

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsStreaming(true);

      streamMessage(
        sessionId,
        message,
        (token) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              updated[updated.length - 1] = { ...last, content: last.content + token };
            }
            return updated;
          });
        },
        () => setIsStreaming(false),
        (err) => {
          console.error("Stream error:", err);
          setIsStreaming(false);
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant" && !last.content) {
              updated[updated.length - 1] = {
                ...last,
                content: "Sorry, something went wrong. Please try again.",
              };
            }
            return updated;
          });
        },
        (metadata) => {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                citations: metadata.citations,
              };
            }
            return updated;
          });
        }
      );
    },
    [sessionId]
  );

  function handleNewChat() {
    setAppState("idle");
    setSessionId(null);
    setMessages([]);
    setVideoA(undefined);
    setVideoB(undefined);
    setTranscriptA(undefined);
    setTranscriptB(undefined);
    setUrlA("");
    setUrlB("");
  }

  const handleSelectSession = useCallback(async (id: string) => {
    setAppState("loading");
    try {
      const data = await getSessionDetails(id);
      setSessionId(id);
      
      // Normalize videos from the backend data
      const videoA = normalizeVideoPayload("A", data.videos?.A);
      const videoB = normalizeVideoPayload("B", data.videos?.B);
      
      setVideoA(videoA?.metadata);
      setVideoB(videoB?.metadata);
      setTranscriptA(videoA?.transcript);
      setTranscriptB(videoB?.transcript);
      
      // Load URLs
      setUrlA(videoA?.metadata?.video_id ? `https://www.youtube.com/watch?v=${videoA.metadata.video_id}` : "");
      setUrlB(videoB?.metadata?.video_id ? `https://www.youtube.com/watch?v=${videoB.metadata.video_id}` : "");

      // Load chat history
      if (data.history && data.history.length > 0) {
        const loadedMessages: ChatMessage[] = [];
        data.history.forEach((turn: any, index: number) => {
          if (turn.question && turn.question !== "unknown") {
            loadedMessages.push({
              id: `msg-u-${index}`,
              role: "user",
              content: turn.question,
              timestamp: new Date(turn.timestamp || Date.now()),
            });
          }
          if (turn.final_answer) {
            loadedMessages.push({
              id: `msg-a-${index}`,
              role: "assistant",
              content: turn.final_answer,
              citations: turn.transcript_chunks_retrieved || [],
              timestamp: new Date(turn.timestamp || Date.now()),
            });
          }
        });
        setMessages(loadedMessages);
      } else {
        setMessages([]);
      }
      
      setAppState("ready");
    } catch (error) {
      console.error("Failed to load session:", error);
      setAppState("idle");
    }
  }, []);

  const handleDeleteSession = useCallback(async (id: string) => {
    try {
      await deleteSession(id);
      if (sessionId === id) {
        handleNewChat();
      }
      const updatedSessions = await getSessions();
      setSessions(updatedSessions);
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  }, [sessionId]);

  const hasMessages = messages.length > 0;
  const showThreePanel = hasMessages && !isChatMinimized;

  return (
    <div className="relative flex h-[100dvh] overflow-hidden">
      <IngestModal
        isOpen={showIngestModal}
        results={ingestResults}
        onProceed={handleProceedAnyway}
        onRetry={handleRetry}
        onReplace={handleReplace}
        onCancel={handleCancelIngest}
      />
      <Sidebar
        activeSessionId={sessionId || undefined}
        sessions={sessions}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
        isDark={isDark}
        toggleTheme={toggleTheme}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
      />

      <main
        className={clsx(
          "relative z-10 flex min-w-0 flex-1 flex-col transition-all duration-300",
          !collapsed ? "lg:ml-[280px]" : ""
        )}
        style={{ transitionTimingFunction: "var(--ease-out)" }}
      >
        {/* Cinematic Dimming Overlay */}
        <div 
          className={clsx(
            "absolute inset-0 bg-black/60 backdrop-blur-[3px] transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] pointer-events-none",
            highlightedVideoId ? "opacity-100 z-40" : "opacity-0 -z-10"
          )} 
        />

        <div
          className={clsx(
            "relative flex shrink-0 items-center justify-between gap-4 px-4 py-4 transition-[padding] duration-300 sm:px-6 lg:px-8",
          )}
          style={{
            paddingLeft: collapsed ? "5rem" : undefined,
            transitionTimingFunction: "var(--ease-out)",
          }}
        >
          <div className="min-w-0">
            <h1 className="truncate text-xl font-semibold tracking-[-0.02em] text-[var(--text-primary)] sm:text-2xl">
              Content Analyzer
            </h1>
          </div>

          <button
            onClick={toggleTheme}
            className="rounded-[var(--radius-md)] glass-surface p-2.5 press-scale cursor-pointer"
            style={{ transitionDuration: "120ms" }}
            aria-label="Toggle dark mode"
          >
            {isDark ? (
              <Sun size={18} className="text-[var(--text-secondary)]" />
            ) : (
              <Moon size={18} className="text-[var(--text-secondary)]" />
            )}
          </button>

          {hasMessages && (
            <div className="absolute left-1/2 top-1/2 z-20 flex -translate-x-1/2 -translate-y-1/2 items-center">
              <button
                onClick={() => setIsChatMinimized(!isChatMinimized)}
                className="flex items-center gap-1.5 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-glass-strong)] px-3.5 py-1.5 text-xs font-semibold text-[var(--text-secondary)] shadow-sm backdrop-blur-md transition-all hover:bg-[var(--bg-surface-hover)] hover:text-[var(--text-primary)] hover:border-[var(--border)] press-scale cursor-pointer"
              >
                {isChatMinimized ? (
                  <>
                    <SidebarSimple size={15} weight="bold" />
                    <span>3 Panel View</span>
                  </>
                ) : (
                  <>
                    <ArrowsInSimple size={15} weight="bold" />
                    <span>2 Panel View</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        <div className="relative flex-1 w-full overflow-hidden flex flex-col">
          {/* Main Grid Container */}
          <div 
            className={clsx(
              "w-full mx-auto transition-all duration-700 ease-[var(--ease-in-out)] h-full px-4 sm:px-6 lg:px-8",
              (!showThreePanel && appState !== "idle") ? "pb-28" : "pb-4"
            )}
            style={{
               maxWidth: showThreePanel ? "1700px" : "1240px",
               paddingTop: (!showThreePanel && appState === "idle") ? "22vh" : "1.25rem"
            }}
          >
             {appState === "loading" ? (
                <ComparisonSkeleton />
             ) : (
                <div className="flex h-full transition-all duration-700 ease-[var(--ease-in-out)] gap-5">
                  {/* Video A */}
                  <div 
                    className={clsx(
                      "h-full overflow-y-auto hide-scrollbar rounded-[var(--radius-2xl)] min-w-0 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
                      videoA?.video_id === highlightedVideoId ? "relative z-50 scale-[1.03]" : "scale-100"
                    )}
                    style={{ width: showThreePanel ? "22%" : "50%" }}
                  >
                     <VideoCard 
                       label="A" 
                       url={urlA} 
                       onUrlChange={setUrlA} 
                       metadata={videoA} 
                       transcript={transcriptA} 
                       seekRequest={seekRequestA} 
                       isHighlighted={videoA?.video_id === highlightedVideoId}
                     />
                  </div>

                  {/* Chat Panel (Middle) */}
                  <div 
                    className="h-full relative overflow-hidden transition-all duration-700 ease-[var(--ease-in-out)]"
                    style={{ width: showThreePanel ? "56%" : "0%" }}
                  >
                     <div className={clsx(
                       "absolute inset-0 w-full h-full transition-all duration-700 ease-[var(--ease-in-out)] flex flex-col min-h-0",
                       showThreePanel ? "opacity-100 translate-y-0 delay-500" : "opacity-0 translate-y-24 pointer-events-none"
                     )}>
                        <ChatPanel
                           messages={messages}
                           onSend={handleSend}
                           isStreaming={isStreaming}
                           appState={appState}
                           canCompare={Boolean(urlA.trim() && urlB.trim())}
                           onCompare={handleCompare}
                           onCitationClick={handleCitationClick}
                           onVideoHighlightClick={handleVideoHighlightClick}
                           videoContexts={videoContexts}
                        />
                     </div>
                  </div>

                  {/* Video B */}
                  <div 
                    className={clsx(
                      "h-full overflow-y-auto hide-scrollbar rounded-[var(--radius-2xl)] min-w-0 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
                      videoB?.video_id === highlightedVideoId ? "relative z-50 scale-[1.03]" : "scale-100"
                    )}
                    style={{ width: showThreePanel ? "22%" : "50%" }}
                  >
                     <VideoCard 
                       label="B" 
                       url={urlB} 
                       onUrlChange={setUrlB} 
                       metadata={videoB} 
                       transcript={transcriptB} 
                       seekRequest={seekRequestB}
                       isHighlighted={videoB?.video_id === highlightedVideoId}
                     />
                  </div>
                </div>
             )}
          </div>

          {/* Chat Panel (Bottom - Idle) */}
          <div className={clsx(
            "absolute bottom-0 left-0 w-full flex justify-center px-4 sm:px-6 lg:px-8 pointer-events-none transition-all duration-700 ease-[var(--ease-in-out)] z-20",
            showThreePanel ? "-translate-y-24 opacity-0 delay-500" : "translate-y-0 opacity-100",
            appState === "idle" ? "pb-[22vh] xl:pb-[26vh]" : "pb-5"
          )}>
             <div className={clsx("w-full max-w-[800px]", showThreePanel ? "pointer-events-none" : "pointer-events-auto")}>
                <ChatPanel
                   messages={[]}
                   onSend={(msg) => {
                     setIsChatMinimized(false);
                     handleSend(msg);
                   }}
                   isStreaming={isStreaming}
                   appState={appState}
                   canCompare={Boolean(urlA.trim() && urlB.trim())}
                   onCompare={handleCompare}
                   onCitationClick={handleCitationClick}
                   onVideoHighlightClick={handleVideoHighlightClick}
                   videoContexts={videoContexts}
                />
             </div>
          </div>
        </div>
      </main>
    </div>
  );
}
