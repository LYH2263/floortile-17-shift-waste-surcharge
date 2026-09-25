async function request(path, options) {
  const r = await fetch(path, options)
  if (!r.ok) throw new Error(await r.text())
  return r.status === 204 ? null : r.json()
}

export function getJSON(path) {
  return request(path)
}
export function postJSON(path, body) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
}
export function putJSON(path, body) {
  return request(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}
export function deleteJSON(path) {
  return request(path, { method: 'DELETE' })
}

/** "HH:MM" -> decimal hour, e.g. "22:30" -> 22.5; empty -> null */
export function timeToHour(value) {
  if (!value) return null
  const [h, m] = value.split(':').map(Number)
  return h + (m || 0) / 60
}

/** decimal hour -> "HH:MM" */
export function hourToTime(value) {
  if (value === null || value === undefined) return ''
  const t = ((value % 24) + 24) % 24
  const h = Math.floor(t)
  const m = Math.round((t - h) * 60)
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}
