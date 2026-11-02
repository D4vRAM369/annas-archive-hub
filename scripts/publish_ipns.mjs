// Publica el CID actual (data/ipfs_hash.txt) bajo un nombre IPNS fijo.
// Clave: variable de entorno IPNS_KEY (64 bytes ed25519 en base64). Sin ella, no hace nada.
import * as Name from 'w3name'
import { readFileSync } from 'node:fs'

const key = process.env.IPNS_KEY
if (!key) { console.log('[ipns] IPNS_KEY no definido, se omite'); process.exit(0) }

const cid = readFileSync(new URL('../data/ipfs_hash.txt', import.meta.url), 'utf8').trim()
const value = `/ipfs/${cid}`
const name = await Name.from(Buffer.from(key, 'base64'))

let revision
try {
  const current = await Name.resolve(name)
  if (current.value === value) { console.log(`[ipns] ${name} ya apunta a ${cid}`); process.exit(0) }
  revision = await Name.increment(current, value)
} catch (e) {
  if (!/not found|404|no record/i.test(String(e?.message))) throw e // error real: no publicar con seq 0
  revision = await Name.v0(name, value) // primera publicación
}
await Name.publish(revision, name.key)
console.log(`[ipns] ${name} -> ${cid} (seq ${revision.sequence})`)
