import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// --- VIDEOS ---
export const saveVideo = mutation({
  args: { video_id: v.string(), payload: v.any() },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("videos")
      .withIndex("by_video_id", (q) => q.eq("video_id", args.video_id))
      .first();
    
    if (existing) {
      await ctx.db.patch(existing._id, {
        metadata: args.payload.metadata,
        transcript: args.payload.transcript,
        timestamp: args.payload.timestamp,
      });
    } else {
      await ctx.db.insert("videos", {
        video_id: args.video_id,
        metadata: args.payload.metadata,
        transcript: args.payload.transcript,
        timestamp: args.payload.timestamp,
      });
    }
  },
});

export const getVideo = query({
  args: { video_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("videos")
      .withIndex("by_video_id", (q) => q.eq("video_id", args.video_id))
      .first();
  },
});

// --- SESSIONS ---
export const createSession = mutation({
  args: {
    session_id: v.string(),
    video_ids: v.array(v.string()),
    labels: v.any(),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("sessions", {
      session_id: args.session_id,
      video_ids: args.video_ids,
      labels: args.labels,
      timestamp: Date.now(),
    });
  },
});

export const getSession = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});

export const listSessions = query({
  handler: async (ctx) => {
    const sessions = await ctx.db.query("sessions").order("desc").collect();
    return sessions;
  },
});

// --- LOGS ---
export const saveLog = mutation({
  args: { session_id: v.string(), turns: v.array(v.any()) },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("logs")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
      
    if (existing) {
      await ctx.db.patch(existing._id, { turns: args.turns });
    } else {
      await ctx.db.insert("logs", {
        session_id: args.session_id,
        turns: args.turns,
      });
    }
  },
});

export const getLog = query({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("logs")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
  },
});

export const deleteSession = mutation({
  args: { session_id: v.string() },
  handler: async (ctx, args) => {
    const session = await ctx.db
      .query("sessions")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();

    if (!session) return;

    // Delete logs
    const log = await ctx.db
      .query("logs")
      .withIndex("by_session_id", (q) => q.eq("session_id", args.session_id))
      .first();
    if (log) {
      await ctx.db.delete(log._id);
    }

    // Delete video details
    if (session.video_ids && session.video_ids.length > 0) {
      for (const video_id of session.video_ids) {
        const video = await ctx.db
          .query("videos")
          .withIndex("by_video_id", (q) => q.eq("video_id", video_id))
          .first();
        if (video) {
          await ctx.db.delete(video._id);
        }
      }
    }

    // Delete session
    await ctx.db.delete(session._id);
  },
});
