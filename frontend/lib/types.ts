/* ─── Video Metadata ─── */
export interface VideoMetadata {
  video_id: string;
  title: string;
  creator: string;
  creator_avatar?: string;
  subscriber_count?: string;
  duration?: string;
  upload_date?: string;
  thumbnail_url?: string;
  view_count?: string;
  like_count?: string;
  comment_count?: string;
  engagement_rate?: string;
  hashtags?: string[];
  verified?: boolean;
}

/* ─── Transcript ─── */
export interface TranscriptSegment {
  start_time: string;
  end_time?: string;
  text: string;
}

/* ─── Ingest ─── */
export interface IngestResult {
  url: string;
  status: "success" | "error";
  upserted_count?: number;
  message?: string;
}

export interface VideoPayload {
  video_id: string;
  metadata: VideoMetadata;
  transcript: TranscriptSegment[];
}

export interface IngestResponse {
  session_id: string;
  results: IngestResult[];
  videos?: Partial<Record<"A" | "B", VideoPayload>>;
}

/* ─── Chat ─── */
export interface Citation {
  video_id: string;
  chunk_index: number;
  start_time: string;
  end_time: string;
  text: string;
  chunk_text?: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

/* ─── Session ─── */
export interface SessionManifest {
  session_id: string;
  video_ids: string[];
  labels: Record<string, string>;
}

/* ─── Sidebar session entries (placeholder) ─── */
export interface SessionEntry {
  id: string;
  title: string;
  subtitle?: string;
  date: string;
}
