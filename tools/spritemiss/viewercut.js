const gfxRefTileHashCache = new Map();
let _descHashSet = null;

function fnv1a_64(bytes, offset, length) {
  let hash = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n;
  const mask = 0xFFFFFFFFFFFFFFFFn;
  for (let i = 0; i < length; i++) {
    hash ^= BigInt(bytes[offset + i]);
    hash = (hash * prime) & mask;
  }
  return hash;
}

function snesAddrToFile(addr) {
  const bank = (addr >> 16) & 0xFF;
  const offset = addr & 0xFFFF;
  return ((bank & 0x3F) << 16) | offset;
}

function loadSpriteDescriptor(rom, gfxRef) {
  const descTableAddr = 0x3C8000; // DATA_BC8000 in file
  if (descTableAddr + gfxRef + 3 >= rom.size) return null;

  // Read 24-bit SNES address from the pointer table
  const lo = rom.readByteAt(descTableAddr + gfxRef);
  const mid = rom.readByteAt(descTableAddr + gfxRef + 1);
  const hi = rom.readByteAt(descTableAddr + gfxRef + 2);
  const snesAddr = (hi << 16) | (mid << 8) | lo;
  if (snesAddr === 0) return null;
  const fileOffset = snesAddrToFile(snesAddr);
  if (fileOffset + 8 >= rom.size) return null;

  // Always read full 8-byte header
  rom.seek(fileOffset);
  const big16Count = rom.readByte();   // byte 0: count of 16x16 OAM entries
  const small8Count = rom.readByte();  // byte 1: count of 8x8 OAM entries
  const tileBase = rom.readByte();     // byte 2: tile name base
  const extraCount = rom.readByte();   // byte 3: extra displacement count
  const flags = rom.readByte();        // byte 4: attributes
  const block1Tiles = rom.readByte();  // byte 5: first DMA block tile count
  const region2Offset = rom.readByte();// byte 6: second region VRAM offset
  const block2Tiles = rom.readByte() & 0x0F; // byte 7: second DMA block tile count

  const totalDisp = big16Count + small8Count + extraCount;
  if (totalDisp === 0 || totalDisp > 128) return null;

  // Read displacement pairs (order: 16x16 entries first, then 8x8, then extra)
  const entries = [];
  for (let i = 0; i < totalDisp; i++) {
    if (rom.getPosition() + 2 > rom.size) break;
    const rawX = rom.readByte();
    const rawY = rom.readByte();
    const is16x16 = (i < big16Count);
    const size = is16x16 ? 16 : 8;
    entries.push({ tx: rawX - 0x80, ty: rawY - 0x80, size });
  }

  // Read CHR tile data (immediately after displacements)
  const block1Size = block1Tiles * 32;
  const block2Size = block2Tiles * 32;
  let chrBlock1 = null, chrBlock2 = null;

  if (block1Size > 0 && rom.getPosition() + block1Size <= rom.size) {
    chrBlock1 = rom.readBytes(block1Size);
  }
  if (block2Size > 0 && rom.getPosition() + block2Size <= rom.size) {
    chrBlock2 = rom.readBytes(block2Size);
  }

  return { big16Count, small8Count, extraCount, tileBase, flags, entries,
           block1Tiles, block2Tiles, region2Offset, chrBlock1, chrBlock2 };
}

function gfxRefTileHashes(rom, gfxRef) {
  if (gfxRefTileHashCache.has(gfxRef)) return gfxRefTileHashCache.get(gfxRef);
  const out = [];
  const desc = loadSpriteDescriptor(rom, gfxRef);
  if (desc) {
    for (const blk of [desc.chrBlock1, desc.chrBlock2]) {
      if (!blk) continue;
      for (let off = 0; off + 32 <= blk.length; off += 32) {
        out.push(fnv1a_64(blk, off, 32).toString(16).padStart(16, '0').toUpperCase());
      }
    }
  }
  gfxRefTileHashCache.set(gfxRef, out);
  return out;
}

function descriptorTileHashes(rom) {
  if (_descHashSet) return _descHashSet;
  if (!rom) return null;
  const t0 = performance.now();
  const s = new Set();
  let refs = 0;
  for (let g = 0; g < 0x8000; g += 4) {
    const hs = gfxRefTileHashes(rom, g);
    if (hs.length) refs++;
    for (const h of hs) s.add(h);
  }
  _descHashSet = s;
  console.log(`[laufzeit] ${s.size} Kachel-Hashes aus ${refs} Sprite-Deskriptoren ` +
              `(${Math.round(performance.now() - t0)} ms) — Objekte, die NUR daraus bestehen, ` +
              `gehören in die Sprite-Galerie und werden ausgeblendet.`);
  return s;
}