import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // Stores session metadata (which videos are in this session)
  sessions: defineTable({
    session_id: v.string(),
    video_ids: v.array(v.string()),
    labels: v.any(), // Map of video_id to label ("A" or "B")
    title: v.optional(v.string()),
    date: v.optional(v.string()),
    timestamp: v.optional(v.number()),
  }).index("by_session_id", ["session_id"]),

  // Stores the video transcripts and metadata
  videos: defineTable({
    video_id: v.string(),
    metadata: v.any(),
    transcript: v.any(),
    timestamp: v.optional(v.string()),
  }).index("by_video_id", ["video_id"]),

  // Stores the chat history for a session
  logs: defineTable({
    session_id: v.string(),
    turns: v.array(v.any()), 
  }).index("by_session_id", ["session_id"]),
});
