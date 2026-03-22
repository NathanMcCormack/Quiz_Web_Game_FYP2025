export async function fetchLegacyHistory() {
  const res = await fetch("/api/daily/history");
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`fetchLegacyHistory failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function fetchLegacyChallenge(dateStr) {
  const res = await fetch(`/api/daily/history/${dateStr}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`fetchLegacyChallenge failed: ${res.status} ${text}`);
  }
  return res.json();
}