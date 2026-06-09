import type {
  ChatResponse,
  IngestResponse,
  TranscriptSegment,
  VideoPayload,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/* ─── Ingest ─── */
export async function ingestVideos(
  urlA: string,
  urlB: string
): Promise<IngestResponse> {
  const res = await fetch(`${BASE_URL}/api/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url_a: urlA, url_b: urlB }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Ingest failed: ${err}`);
  }
  const payload = await res.json();
  return normalizeIngestResponse(payload);
}

export async function confirmIngest(sessionId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/confirm_ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Confirm Ingest failed: ${err}`);
  }
  return res.json();
}

interface RawVideoPayload {
  video_id?: string;
  metadata?: RawVideoMetadata | null;
  transcript?: RawTranscriptSegment[];
}

interface RawVideoMetadata {
  title?: string | null;
  creator?: string | null;
  subscribercount?: number | string | null;
  subscriber_count?: number | string | null;
  duration?: string | null;
  upload_date?: string | null;
  thumbnail_url?: string | null;
  profile_url?: string | null;
  views?: number | string | null;
  view_count?: number | string | null;
  likes?: number | string | null;
  comments?: number | string | null;
  engagement_rate?: number | string | null;
  hashtags?: string[] | string | null;
}

interface RawTranscriptSegment {
  text?: string;
  start?: number;
  duration?: number;
  end?: number;
  start_time?: string;
  end_time?: string;
}

interface RawIngestResponse {
  session_id: string;
  results: IngestResponse["results"];
  videos?: Partial<Record<"A" | "B", RawVideoPayload | null>>;
}

function normalizeIngestResponse(payload: RawIngestResponse): IngestResponse {
  return {
    ...payload,
    videos: {
      A: normalizeVideoPayload("A", payload.videos?.A),
      B: normalizeVideoPayload("B", payload.videos?.B),
    },
  };
}

export function normalizeVideoPayload(
  label: "A" | "B",
  payload?: RawVideoPayload | null
): VideoPayload | undefined {
  if (!payload) return undefined;

  const metadata = payload.metadata ?? {};
  const videoId = payload.video_id ?? "";
  const subscriberCount = metadata.subscribercount ?? metadata.subscriber_count;
  const viewCount = metadata.views ?? metadata.view_count;

  return {
    video_id: videoId,
    metadata: {
      video_id: videoId,
      title: metadata.title ?? `Video ${label}`,
      creator: metadata.creator ?? "Unknown creator",
      creator_avatar: metadata.profile_url ?? undefined,
      subscriber_count: formatCount(subscriberCount, "subscribers"),
      duration: formatIsoDuration(metadata.duration),
      upload_date: formatDate(metadata.upload_date),
      thumbnail_url: metadata.thumbnail_url ?? undefined,
      view_count: formatCount(viewCount, "views"),
      like_count: formatCount(metadata.likes, "likes"),
      comment_count: formatCount(metadata.comments, "comments"),
      engagement_rate: formatPercent(metadata.engagement_rate, "engagement"),
      hashtags: normalizeTags(metadata.hashtags),
      verified: false,
    },
    transcript: normalizeTranscript(payload.transcript),
  };
}

function normalizeTranscript(segments?: RawTranscriptSegment[]): TranscriptSegment[] {
  if (!Array.isArray(segments)) return [];

  return segments
    .filter((segment) => segment.text)
    .map((segment) => {
      const start = typeof segment.start === "number" ? segment.start : 0;
      const end =
        typeof segment.end === "number"
          ? segment.end
          : typeof segment.duration === "number"
            ? start + segment.duration
            : undefined;

      return {
        start_time: segment.start_time ?? formatTimestamp(start),
        end_time: segment.end_time ?? (typeof end === "number" ? formatTimestamp(end) : undefined),
        text: segment.text ?? "",
      };
    });
}

function normalizeTags(tags?: string[] | string | null): string[] {
  if (!Array.isArray(tags)) return [];
  return tags.map((tag) => tag.trim()).filter(Boolean).slice(0, 8);
}

function formatCount(value: number | string | null | undefined, label: string): string | undefined {
  const numberValue = Number(value);
  if (!Number.isFinite(numberValue)) return undefined;

  const formatted = new Intl.NumberFormat("en", {
    notation: "compact",
    maximumFractionDigits: numberValue >= 1000 ? 1 : 0,
  }).format(numberValue);

  return `${formatted} ${label}`;
}

function formatPercent(value: number | string | null | undefined, label: string): string | undefined {
  const numberValue = Number(value);
  if (!Number.isFinite(numberValue)) return undefined;
  return `${numberValue.toFixed(2)}% ${label}`;
}

function formatDate(value?: string | null): string | undefined {
  if (!value) return undefined;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function formatIsoDuration(value?: string | null): string | undefined {
  if (!value) return undefined;

  const match = value.match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!match) return value;

  const hours = Number(match[1] ?? 0);
  const minutes = Number(match[2] ?? 0);
  const seconds = Number(match[3] ?? 0);

  return [hours, minutes, seconds]
    .filter((part, index) => index > 0 || part > 0)
    .map((part, index) => (index === 0 ? String(part) : String(part).padStart(2, "0")))
    .join(":");
}

function formatTimestamp(seconds: number): string {
  const safeSeconds = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const remainingSeconds = safeSeconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
}

/* ─── Chat (single response) ─── */
export async function sendMessage(
  sessionId: string,
  message: string
): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Chat failed: ${err}`);
  }
  return res.json();
}

/* ─── Chat (streaming via SSE) ─── */
export async function streamMessage(
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (error: Error) => void,
  onMetadata?: (metadata: any) => void
): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Stream failed: ${err}`);
    }

    const reader = res.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";
    let eventData: string[] = [];
    let eventName: string | null = null;

    function flushEvent() {
      if (eventData.length === 0) return;
      const data = eventData.join("\n");
      eventData = [];
      
      const currentEventName = eventName;
      eventName = null;

      if (data === "[DONE]") {
        onDone();
        return "done";
      }

      if (currentEventName === "metadata" && onMetadata) {
        try {
          const parsed = JSON.parse(data);
          onMetadata(parsed);
        } catch (e) {
          console.error("Failed to parse metadata", e);
        }
      } else {
        onToken(data);
      }
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const normalizedLine = line.endsWith("\r") ? line.slice(0, -1) : line;
        if (normalizedLine === "") {
          if (flushEvent() === "done") {
            return;
          }
          continue;
        }

        if (normalizedLine.startsWith("event:")) {
          eventName = normalizedLine.slice(6).trim();
          continue;
        }

        if (!normalizedLine.startsWith("data:")) continue;
        eventData.push(
          normalizedLine.startsWith("data: ")
            ? normalizedLine.slice(6)
            : normalizedLine.slice(5)
        );
      }
    }
    if (buffer.startsWith("data:")) {
      eventData.push(buffer.slice(5));
    }
    if (flushEvent() === "done") {
      return;
    }
    onDone();
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
  }
}

/* ─── Sessions ─── */
export async function getSessions(): Promise<any[]> {
  const res = await fetch(`${BASE_URL}/api/sessions`);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to fetch sessions: ${err}`);
  }
  return res.json();
}

export async function getSessionDetails(sessionId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to fetch session: ${err}`);
  }
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Failed to delete session: ${err}`);
  }
  return res.json();
}
