"use client";

import VideoCard from "./VideoCard";
import type { VideoMetadata, TranscriptSegment } from "@/lib/types";

interface VideoComparisonProps {
  urlA: string;
  urlB: string;
  onUrlAChange: (val: string) => void;
  onUrlBChange: (val: string) => void;
  videoA?: VideoMetadata;
  videoB?: VideoMetadata;
  transcriptA?: TranscriptSegment[];
  transcriptB?: TranscriptSegment[];
}

export default function VideoComparison({
  urlA,
  urlB,
  onUrlAChange,
  onUrlBChange,
  videoA,
  videoB,
  transcriptA,
  transcriptB,
}: VideoComparisonProps) {
  return (
    <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-2">
      <VideoCard label="A" url={urlA} onUrlChange={onUrlAChange} metadata={videoA} transcript={transcriptA} />
      <VideoCard label="B" url={urlB} onUrlChange={onUrlBChange} metadata={videoB} transcript={transcriptB} />
    </div>
  );
}
