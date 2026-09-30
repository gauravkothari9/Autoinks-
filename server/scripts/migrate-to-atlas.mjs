// Copy every collection (documents + indexes) from one MongoDB database to another.
// Usage: SOURCE_URI=... TARGET_URI=... DB_NAME=stick-reels node scripts/migrate-to-atlas.mjs
// Refuses to write into a collection that already has documents, so it never duplicates data.
import mongoose from 'mongoose';

const { MongoClient } = mongoose.mongo;

const { SOURCE_URI, TARGET_URI, DB_NAME = 'stick-reels' } = process.env;
if (!SOURCE_URI || !TARGET_URI) {
  console.error('Set SOURCE_URI and TARGET_URI');
  process.exit(1);
}

const source = new MongoClient(SOURCE_URI);
const target = new MongoClient(TARGET_URI, { serverSelectionTimeoutMS: 15000 });
await source.connect();
await target.connect();
const from = source.db(DB_NAME);
const to = target.db(DB_NAME);
console.log(`Connected. Copying "${DB_NAME}" …`);

let problems = 0;
for (const { name, type } of await from.listCollections().toArray()) {
  if (type !== 'collection' || name.startsWith('system.')) continue;
  const src = from.collection(name);
  const dst = to.collection(name);
  const existing = await dst.estimatedDocumentCount();
  if (existing > 0) {
    console.log(`  ${name}: SKIPPED, target already has ${existing} documents`);
    problems++;
    continue;
  }
  const docs = await src.find().toArray();
  if (docs.length) await dst.insertMany(docs, { ordered: true });

  for (const idx of await src.indexes()) {
    if (idx.name === '_id_') continue;
    const { key, name: idxName, v, ns, ...options } = idx;
    await dst.createIndex(key, { name: idxName, ...options });
  }
  const copied = await dst.countDocuments();
  const ok = copied === docs.length;
  if (!ok) problems++;
  console.log(`  ${name}: ${docs.length} → ${copied} ${ok ? 'OK' : 'MISMATCH'}`);
}

await source.close();
await target.close();
console.log(problems ? `Finished with ${problems} problem(s).` : 'All collections copied and verified.');
process.exit(problems ? 1 : 0);
