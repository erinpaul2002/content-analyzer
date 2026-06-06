export function parseTimeToSeconds(timeInput: string | number): number {
  if (timeInput == null) return 0;
  if (typeof timeInput === 'number') return timeInput;
  
  const timeStr = String(timeInput);
  const parts = timeStr.split(':').map(Number);
  let seconds = 0;
  if (parts.length === 3) {
    seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
  } else if (parts.length === 2) {
    seconds = parts[0] * 60 + parts[1];
  } else if (parts.length === 1) {
    seconds = parts[0] || 0;
  }
  return seconds;
}
