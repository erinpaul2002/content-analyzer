/**
 * Welcome to Cloudflare Workers! This is your first worker.
 *
 * - Run `npm run dev` in your terminal to start a development server
 * - Open a browser tab at http://localhost:8787/ to see your worker in action
 * - Run `npm run deploy` to publish your worker
 *
 * Bind resources to your worker in `wrangler.jsonc`. After adding bindings, a type definition for the
 * `Env` object can be regenerated with `npm run cf-typegen`.
 *
 * Learn more at https://developers.cloudflare.com/workers/
 */
export interface Env {
	WORKER_TOKEN: string;
}

import { YoutubeTranscript } from 'youtube-transcript';

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		if (request.method !== "POST") {
			return new Response(JSON.stringify({
				error: "Method not allowed",
			}), { status: 405 });
		}

		const token = request.headers.get("X-Worker-Token");
		if (!env.WORKER_TOKEN || token !== env.WORKER_TOKEN) {
			return new Response(JSON.stringify({
				error: "Unauthorized"
			}), { status: 401 });
		}

		try {
			const body = await request.json() as any;
			const { url, languages = ["en", "en-US"] } = body;

			if (!url) {
				return new Response(JSON.stringify({
					error: "Missing video URL"
				}), { status: 400 });
			}

			const videoIdMatch = url.match(/(?:v=|\/)([0-9A-Za-z_-]{11}).*/);
			const videoId = videoIdMatch ? videoIdMatch[1] : null;

			if (!videoId) {
				return new Response(JSON.stringify({
					error: "Invaid video ID"
				}), { status: 400 });
			}

			const transcriptData = await YoutubeTranscript.fetchTranscript(videoId, { lang: languages[0] });

			if (!transcriptData || transcriptData.length === 0) {
				throw new Error("No transcripts found via youtube-transcript library");
			}

			const transcript = transcriptData.map((t, index) => ({
				id: index,
				text: t.text,
				start: t.offset / 1000.0,
				duration: t.duration / 1000.0
			}));

			let languageCode = transcriptData[0]?.lang || languages[0];

			return new Response(JSON.stringify({
				videoId: videoId,
				language: languageCode,
				transcript: transcript
			}), {
				headers: { "Content-Type": "application/json" }
			});
		} catch (err: any) {
			return new Response(JSON.stringify({ error: err.message, stack: err.stack }), {
				status: 500,
				headers: { "Content-Type": "application/json" }
			});
		}
	}
} satisfies ExportedHandler<Env>;
