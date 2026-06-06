"use client";

import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { parseTimeToSeconds } from "@/lib/utils";
import {
  CalendarBlank,
  CaretDown,
  ChatCircle,
  ChartLine,
  Clock,
  CornersOut,
  DotsThree,
  Eye,
  FileText,
  GearSix,
  LinkSimple,
  Play,
  SealCheck,
  SpeakerHigh,
  ThumbsUp,
} from "@phosphor-icons/react";
import type { VideoMetadata, TranscriptSegment } from "@/lib/types";

interface VideoCardProps {
  label: "A" | "B";
  url: string;
  onUrlChange: (url: string) => void;
  metadata?: VideoMetadata;
  transcript?: TranscriptSegment[];
  seekRequest?: { time: number; t: number } | null;
  isHighlighted?: boolean;
}

export default function VideoCard({
  label,
  url,
  onUrlChange,
  metadata,
  transcript = [],
  seekRequest,
  isHighlighted,
}: VideoCardProps) {
  const [showFull, setShowFull] = useState(false);
  const [isPlayerOpen, setIsPlayerOpen] = useState(true);
  const [isMetadataOpen, setIsMetadataOpen] = useState(false);
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (seekRequest && iframeRef.current?.contentWindow) {
      if (!isPlayerOpen) setIsPlayerOpen(true);
      iframeRef.current.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func: 'seekTo', args: [seekRequest.time, true] }),
        '*'
      );
      iframeRef.current.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func: 'playVideo', args: [] }),
        '*'
      );
    }
  }, [seekRequest, isPlayerOpen]);

  const handleTranscriptClick = (startTime: string) => {
    const seconds = parseTimeToSeconds(startTime);
    if (iframeRef.current?.contentWindow) {
      if (!isPlayerOpen) setIsPlayerOpen(true);
      iframeRef.current.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func: 'seekTo', args: [seconds, true] }),
        '*'
      );
      iframeRef.current.contentWindow.postMessage(
        JSON.stringify({ event: 'command', func: 'playVideo', args: [] }),
        '*'
      );
    }
  };

  const displayMeta: VideoMetadata = metadata ?? {
    video_id: "",
    title: `Video ${label}`,
    creator: "Details unavailable",
    verified: false,
  };

  const visibleTranscript = showFull ? transcript : transcript.slice(0, 4);
  const hasRealVideo = Boolean(displayMeta.video_id);
  const stats = [
    { icon: Clock, label: "Duration", value: displayMeta.duration },
    { icon: CalendarBlank, label: "Published", value: displayMeta.upload_date },
    { icon: Eye, label: "Views", value: displayMeta.view_count },
    { icon: ThumbsUp, label: "Likes", value: displayMeta.like_count },
    { icon: ChatCircle, label: "Comments", value: displayMeta.comment_count },
    { icon: ChartLine, label: "Engagement", value: displayMeta.engagement_rate },
  ].filter((stat) => stat.value);

  return (
    <article className={`overflow-hidden rounded-[var(--radius-2xl)] glass-panel bg-[var(--bg-surface)] transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] ${isHighlighted ? 'ring-2 ring-[var(--accent)] shadow-[0_0_60px_var(--accent-muted)]' : ''}`}>
      {/* URL INPUT SECTION */}
      <div className="border-b border-[var(--border-subtle)] p-4">
        <div
          className="neu-input flex min-h-11 items-center gap-3 rounded-[var(--radius-md)] px-3 transition-all"
          style={{ background: "var(--bg-input)" }}
        >
          <LinkSimple size={17} className="shrink-0 text-[var(--text-tertiary)]" />
          <input
            type="url"
            value={url}
            onChange={(e) => onUrlChange(e.target.value)}
            disabled={hasRealVideo}
            placeholder={`Paste YouTube URL for Video ${label}...`}
            className="min-w-0 flex-1 !bg-transparent text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-tertiary)] disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>

      {hasRealVideo && (
        <>
          {/* SECTION 1: Player & Title */}
          <div className="border-b border-[var(--border-subtle)]">
        <button
          onClick={() => setIsPlayerOpen(!isPlayerOpen)}
          className="flex w-full items-center justify-between p-4 transition-colors hover:bg-[var(--bg-surface-hover)] cursor-pointer"
        >
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--bg-input)] text-xs font-bold text-[var(--text-primary)]">
              {label}
            </span>
            <span className="truncate text-sm font-semibold text-[var(--text-primary)]">
              {displayMeta.title}
            </span>
          </div>
          <CaretDown
            size={16}
            className={`shrink-0 text-[var(--text-tertiary)] transition-transform duration-200 ${
              isPlayerOpen ? "rotate-180" : ""
            }`}
          />
        </button>
        {isPlayerOpen && (
          <div className="pb-5">
            <div className="relative aspect-video overflow-hidden bg-[var(--bg-app)]">
              <span
                className="absolute left-4 top-4 z-10 inline-flex h-10 w-10 items-center justify-center rounded-[var(--radius-lg)] text-sm font-bold text-white neu-button"
                style={{
                  background: "rgba(0,0,0,0.58)",
                  border: "1px solid rgba(255,255,255,0.22)",
                }}
              >
                {label}
              </span>

              {hasRealVideo ? (
                <iframe
                  ref={iframeRef}
                  src={`https://www.youtube-nocookie.com/embed/${displayMeta.video_id}?enablejsapi=1`}
                  title={displayMeta.title}
                  className="h-full w-full border-0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  referrerPolicy="strict-origin-when-cross-origin"
                  allowFullScreen
                />
              ) : displayMeta.thumbnail_url ? (
                <Image
                  src={displayMeta.thumbnail_url}
                  alt={displayMeta.title}
                  fill
                  sizes="(min-width: 1024px) 50vw, 100vw"
                  className="scale-[1.01] object-cover"
                />
              ) : (
                <div className="flex h-full items-center justify-center px-6 text-center text-sm text-[var(--text-tertiary)]">
                  Video details were not returned for this URL.
                </div>
              )}

              {!hasRealVideo && <div className="absolute inset-0 bg-black/10" />}

              {!hasRealVideo && (
                <div className="absolute inset-x-4 bottom-4">
                  <div className="flex items-center gap-3 rounded-[var(--radius-lg)] border border-white/16 bg-black/42 px-3 py-2.5 backdrop-blur-md">
                    <button
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-white text-stone-950 press-scale cursor-pointer"
                      aria-label="Play"
                    >
                      <Play size={16} weight="fill" />
                    </button>
                    <span className="text-[11px] font-medium text-white/82">
                      0:00 / {displayMeta.duration}
                    </span>
                    <div className="relative mx-1 h-1 flex-1 overflow-hidden rounded-sm bg-white/22">
                      <div className="absolute left-0 top-0 h-full w-[18%] rounded-sm bg-white" />
                    </div>
                    <button
                      className="text-white/72 transition-colors hover:text-white press-scale cursor-pointer"
                      aria-label="Volume"
                    >
                      <SpeakerHigh size={16} />
                    </button>
                    <button
                      className="text-white/72 transition-colors hover:text-white press-scale cursor-pointer"
                      aria-label="Settings"
                    >
                      <GearSix size={16} />
                    </button>
                    <button
                      className="text-white/72 transition-colors hover:text-white press-scale cursor-pointer"
                      aria-label="Fullscreen"
                    >
                      <CornersOut size={16} />
                    </button>
                  </div>
                </div>
              )}
            </div>

            <div className="px-5 pt-5">
              <h3 className="mb-4 text-base font-semibold leading-snug tracking-tight text-[var(--text-primary)] line-clamp-2 min-h-[2.75rem]">
                {displayMeta.title}
              </h3>

              <div className="flex items-center gap-3">
                {displayMeta.creator_avatar ? (
                  <Image
                    src={displayMeta.creator_avatar}
                    alt=""
                    width={40}
                    height={40}
                    className="h-10 w-10 shrink-0 rounded-full object-cover"
                  />
                ) : (
                  <div
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold text-[var(--text-secondary)]"
                    style={{ background: "var(--bg-input)" }}
                  >
                    {displayMeta.creator.charAt(0)}
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="truncate text-sm font-medium text-[var(--text-primary)]">
                      {displayMeta.creator}
                    </span>
                    {displayMeta.verified && (
                      <SealCheck size={15} weight="fill" className="shrink-0 text-[var(--accent)]" />
                    )}
                  </div>
                  <p className="text-xs text-[var(--text-tertiary)]">{displayMeta.subscriber_count}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 2: Metadata */}
      <div className="border-b border-[var(--border-subtle)]">
        <button
          onClick={() => setIsMetadataOpen(!isMetadataOpen)}
          className="flex w-full items-center justify-between p-4 transition-colors hover:bg-[var(--bg-surface-hover)] cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <ChartLine size={16} className="text-[var(--text-secondary)]" />
            <span className="text-sm font-semibold text-[var(--text-primary)]">Metadata & Stats</span>
          </div>
          <CaretDown
            size={16}
            className={`shrink-0 text-[var(--text-tertiary)] transition-transform duration-200 ${
              isMetadataOpen ? "rotate-180" : ""
            }`}
          />
        </button>
        {isMetadataOpen && (
          <div className="px-5 pb-5 space-y-4 pt-1">
            {stats.length > 0 && (
              <div className="grid grid-cols-2 border-y border-[var(--border)] sm:grid-cols-3">
                {stats.map((stat) => {
                  const Icon = stat.icon;
                  return (
                    <div
                      key={stat.label}
                      className="border-r border-t border-[var(--border)] px-3 py-3 first:border-t-0 even:border-r-0 sm:[&:nth-child(-n+3)]:border-t-0 sm:[&:nth-child(3n)]:border-r-0"
                    >
                      <div className="mb-1 flex items-center gap-1.5 text-[11px] text-[var(--text-tertiary)]">
                        <Icon size={12} />
                        <span>{stat.label}</span>
                      </div>
                      <p className="truncate text-xs font-medium text-[var(--text-primary)]">
                        {stat.value}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}

            {displayMeta.hashtags && displayMeta.hashtags.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5">
                {displayMeta.hashtags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex min-h-7 items-center rounded-[var(--radius-sm)] px-2.5 text-[11px] font-medium"
                    style={{
                      background: "var(--accent-muted)",
                      color: "var(--accent)",
                      border: "1px solid var(--border)",
                    }}
                  >
                    {tag}
                  </span>
                ))}
                <button
                  className="inline-flex h-7 w-7 items-center justify-center rounded-[var(--radius-sm)] press-scale cursor-pointer hover:bg-[var(--bg-surface-hover)]"
                  style={{ transitionDuration: "120ms" }}
                  aria-label="More tags"
                >
                  <DotsThree size={16} className="text-[var(--text-tertiary)]" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* SECTION 3: Transcript */}
      <div>
        <button
          onClick={() => setIsTranscriptOpen(!isTranscriptOpen)}
          className="flex w-full items-center justify-between p-4 transition-colors hover:bg-[var(--bg-surface-hover)] cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-[var(--text-secondary)]" />
            <span className="text-sm font-semibold text-[var(--text-primary)]">Transcript</span>
          </div>
          <CaretDown
            size={16}
            className={`shrink-0 text-[var(--text-tertiary)] transition-transform duration-200 ${
              isTranscriptOpen ? "rotate-180" : ""
            }`}
          />
        </button>
        {isTranscriptOpen && (
          <div className="px-5 pb-5 pt-1">
            <div className="mb-3 flex items-center justify-between gap-3">
              <span className="text-xs text-[var(--text-tertiary)]">
                {transcript.length} segments
              </span>
              {transcript.length > 4 && (
                <button
                  onClick={() => setShowFull(!showFull)}
                  className="text-xs font-semibold text-[var(--accent)] transition-colors hover:text-[var(--accent-hover)] press-scale cursor-pointer"
                  style={{ transitionDuration: "120ms" }}
                >
                  {showFull ? "Show less" : "Show full"}
                </button>
              )}
            </div>
            <div
              className={`rounded-[var(--radius-md)] bg-[var(--bg-input)] ${
                showFull ? "max-h-[300px] overflow-y-auto" : "overflow-hidden"
              }`}
            >
              {visibleTranscript.length > 0 ? (
                visibleTranscript.map((seg, i) => (
                  <div
                    key={i}
                    onClick={() => handleTranscriptClick(seg.start_time)}
                    className="flex gap-3 border-t border-[var(--border-subtle)] px-3 py-2.5 text-xs first:border-t-0 cursor-pointer hover:bg-[var(--bg-surface-hover)] transition-colors"
                  >
                    <span className="w-10 shrink-0 font-mono text-[var(--accent)]">
                      {seg.start_time}
                    </span>
                    <span className="text-[var(--text-secondary)]">{seg.text}</span>
                  </div>
                ))
              ) : (
                <div className="px-3 py-3 text-xs text-[var(--text-tertiary)]">
                  No transcript segments were returned for this video.
                </div>
              )}
            </div>
          </div>
        )}
          </div>
        </>
      )}
    </article>
  );
}
