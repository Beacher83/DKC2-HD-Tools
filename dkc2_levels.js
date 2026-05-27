// DKC2 Level ID Table (0x00 - 0xBF, 192 entries)
// Source: DKC2 disassembly (p4plus2) + DKC2 level editor (level_name.cpp)
// NULL entries inferred from world/shop patterns
const LEVEL_NAMES = [
  // 0x00 - 0x0F: Main levels + bosses
  null,                                    // 0x00 - Unused/Invalid
  "Glimmer's Galleon",                     // 0x01
  "Rambi Rumble",                          // 0x02
  "Pirate Panic",                          // 0x03
  "Gangplank Galley",                      // 0x04
  "Rattle Battle",                         // 0x05
  "Glimmer's Galleon - Exit",              // 0x06
  "Hot-Head Hop",                          // 0x07
  "Red-Hot Ride",                          // 0x08
  "Krow's Nest",                           // 0x09 (Boss - W1)
  "Slime Climb",                           // 0x0A
  "Topsail Trouble",                       // 0x0B
  "Mainbrace Mayhem",                      // 0x0C
  "Kreepy Krow",                           // 0x0D (Boss - W6)
  "Target Terror",                         // 0x0E
  "Rickety Race",                          // 0x0F

  // 0x10 - 0x1F: More main levels + scenes
  "Haunted Hall",                          // 0x10
  "Hornet Hole",                           // 0x11
  "Rambi Rumble - Rambi Scene",            // 0x12
  "Parrot Chute Panic",                    // 0x13
  "Lava Lagoon",                           // 0x14
  "Lockjaw's Locker",                      // 0x15
  "Fiery Furnace",                         // 0x16
  "Web Woods",                             // 0x17
  "Gusty Glade",                           // 0x18
  "Ghostly Grove",                         // 0x19
  "Topsail Trouble - Shortcut",            // 0x1A
  "K. Rool Cabin",                         // 0x1B
  "Hot-Head Hop - Bonus 2",                // 0x1C
  "Pirate Panic - Shortcut",               // 0x1D
  "Target Terror - End",                   // 0x1E
  "Web Woods - Beta Area",                 // 0x1F

  // 0x20 - 0x2F: More levels + scenes
  "Mainbrace Mayhem - Shortcut",           // 0x20
  "Kleever's Kiln",                        // 0x21 (Boss - W2)
  "Rattle Battle - Rattly Scene",          // 0x22
  "Windy Well",                            // 0x23
  "Squawks's Shaft",                       // 0x24
  "Kannon's Klaim",                        // 0x25
  "Parrot Chute Panic - Shortcut",         // 0x26
  "Kannon's Klaim - Shortcut",             // 0x27
  "Barrel Bayou",                          // 0x28
  "Krockhead Klamber",                     // 0x29
  "Web Woods - Squitter Scene",            // 0x2A
  "Barrel Bayou - Warp Disabled",          // 0x2B
  "Mudhole Marsh",                         // 0x2C
  "Bramble Blast",                         // 0x2D
  "Bramble Scramble",                      // 0x2E
  "Screech's Sprint",                      // 0x2F

  // 0x30 - 0x3F: Overworld maps
  "Overworld - Gangplank Galleon",         // 0x30
  "Overworld - Crocodile Cauldron",        // 0x31
  "Overworld - Krem Quay",                 // 0x32
  "Overworld - Krazy Kremland",            // 0x33
  "Overworld - Gloomy Gulch",              // 0x34
  "Overworld - K. Rool's Keep",            // 0x35
  "Overworld - The Flying Krock",          // 0x36
  "Overworld - Lost World",                // 0x37
  "Overworld - Crocodile Isle",            // 0x38
  null,                                    // 0x39
  null,                                    // 0x3A
  null,                                    // 0x3B
  null,                                    // 0x3C
  null,                                    // 0x3D
  null,                                    // 0x3E
  null,                                    // 0x3F

  // 0x40 - 0x47: Wrinkly Kong's Kollege
  "Wrinkly Kollege - Gangplank Galleon",   // 0x40
  "Wrinkly Kollege - Crocodile Cauldron",  // 0x41
  "Wrinkly Kollege - Krem Quay",           // 0x42
  "Wrinkly Kollege - Krazy Kremland",      // 0x43
  "Wrinkly Kollege - Gloomy Gulch",        // 0x44
  "Wrinkly Kollege - K. Rool's Keep",      // 0x45
  "Wrinkly Kollege - The Flying Krock",    // 0x46
  "Wrinkly Kollege - Lost World",          // 0x47

  // 0x48 - 0x4F: Swanky Kong's Bonus Bonanza
  "Swanky Bonus Bonanza - Gangplank Galleon",   // 0x48
  "Swanky Bonus Bonanza - Crocodile Cauldron",  // 0x49
  "Swanky Bonus Bonanza - Krem Quay",           // 0x4A
  "Swanky Bonus Bonanza - Krazy Kremland",      // 0x4B
  "Swanky Bonus Bonanza - Gloomy Gulch",        // 0x4C
  "Swanky Bonus Bonanza - K. Rool's Keep",      // 0x4D
  "Swanky Bonus Bonanza - The Flying Krock",    // 0x4E
  "Swanky Bonus Bonanza - Lost World",          // 0x4F

  // 0x50 - 0x57: Funky Kong's Flights
  "Funky's Flights - Gangplank Galleon",   // 0x50
  "Funky's Flights - Crocodile Cauldron",  // 0x51
  "Funky's Flights - Krem Quay",           // 0x52
  "Funky's Flights - Krazy Kremland",      // 0x53
  "Funky's Flights - Gloomy Gulch",        // 0x54
  "Funky's Flights - K. Rool's Keep",      // 0x55
  "Funky's Flights - The Flying Krock",    // 0x56
  "Funky's Flights - Lost World",          // 0x57

  // 0x58 - 0x5F: Cranky's Monkey Museum / Klubba's Kiosk
  "Klubba's Kiosk - Gangplank Galleon",    // 0x58
  "Klubba's Kiosk - Crocodile Cauldron",   // 0x59
  "Klubba's Kiosk - Krem Quay",            // 0x5A
  "Klubba's Kiosk - Krazy Kremland",       // 0x5B
  "Klubba's Kiosk - Gloomy Gulch",         // 0x5C
  "Klubba's Kiosk - K. Rool's Keep",       // 0x5D
  "Klubba's Kiosk - The Flying Krock",     // 0x5E
  "Klubba's Kiosk - Lost World",           // 0x5F

  // 0x60 - 0x6F: Bosses, special levels, shortcuts
  "King Zing Sting",                       // 0x60 (Boss - W4)
  "K. Rool Duel",                          // 0x61 (Boss - W7)
  "Castle Crush",                          // 0x62
  "Kudgel's Kontest",                      // 0x63 (Boss - W3)
  null,                                    // 0x64
  null,                                    // 0x65
  null,                                    // 0x66
  null,                                    // 0x67
  "Lockjaw's Locker - Shortcut",           // 0x68
  "Lava Lagoon - Shortcut",               // 0x69
  "Squawks's Shaft - Shortcut",           // 0x6A
  "Krocodile Kore",                        // 0x6B (Boss - W8)
  "Arctic Abyss",                          // 0x6C
  "Chain Link Chamber",                    // 0x6D
  "Toxic Tower",                           // 0x6E

  // 0x6F - 0x7F: Bonus rooms (World 1-2)
  "Pirate Panic - Bonus 1",               // 0x6F
  "Pirate Panic - Bonus 2",               // 0x70
  "Gangplank Galley - Bonus 2",           // 0x71
  "Rattle Battle - Bonus 1",              // 0x72
  "Rattle Battle - Bonus 3",              // 0x73
  "Hot-Head Hop - Bonus 3",               // 0x74
  "Hot-Head Hop - Bonus 1",               // 0x75
  "Red-Hot Ride - Bonus 1",               // 0x76
  "Red-Hot Ride - Bonus 2",               // 0x77
  "Mainbrace Mayhem - Bonus 1",           // 0x78
  "Mainbrace Mayhem - Bonus 2",           // 0x79
  "Slime Climb - Bonus 1",               // 0x7A
  "Topsail Trouble - Bonus 1",            // 0x7B
  "Topsail Trouble - Bonus 2",            // 0x7C
  "Mainbrace Mayhem - Bonus 3",           // 0x7D
  "Slime Climb - Bonus 2",               // 0x7E
  "Rattle Battle - Bonus 2",              // 0x7F

  // 0x80 - 0x8F: More levels + bonuses
  "Klobber Karnage",                       // 0x80
  "Lockjaw's Locker - Bonus 1",           // 0x81
  "Glimmer's Galleon - Bonus 2",          // 0x82
  "Lava Lagoon - Bonus 1",               // 0x83
  "Glimmer's Galleon - Bonus 1",          // 0x84
  "Ghostly Grove - Bonus 1",              // 0x85
  "Gusty Glade - Bonus 1",               // 0x86
  "Gusty Glade - Bonus 2",               // 0x87
  "Ghostly Grove - Bonus 2",              // 0x88
  "Barrel Bayou - Bonus 1",              // 0x89
  "Barrel Bayou - Bonus 2",              // 0x8A
  "Krockhead Klamber - Bonus 1",          // 0x8B
  "Mudhole Marsh - Bonus 1",             // 0x8C
  "Mudhole Marsh - Bonus 2",             // 0x8D
  "Hot-Head Hop / Red-Hot Ride - Shortcut", // 0x8E
  "Clapper's Cavern",                      // 0x8F

  // 0x90 - 0x9F: Animal scenes + bonuses
  "Animal Antics - Enguarde Scene",        // 0x90
  "Clapper's Cavern - Bonus 1",           // 0x91
  "Clapper's Cavern - Bonus 2",           // 0x92
  "Arctic Abyss - Bonus 1",              // 0x93
  "Black Ice Battle - Bonus 1",           // 0x94
  "Arctic Abyss - Bonus 2",              // 0x95
  "Black Ice Battle",                      // 0x96
  "Klobber Karnage - Bonus 1",            // 0x97
  "Jungle Jinx - Bonus 1",               // 0x98
  "Jungle Jinx",                           // 0x99
  "Animal Antics - Rambi Scene",           // 0x9A
  "Animal Antics - Squitter Scene",        // 0x9B
  "Animal Antics - Rattly Scene",          // 0x9C
  "Animal Antics - Bonus 1",              // 0x9D
  "Fiery Furnace - Bonus 1",             // 0x9E
  "Animal Antics - Squawks Scene",         // 0x9F

  // 0xA0 - 0xAF: More bonuses
  "Bramble Blast - Bonus 2",              // 0xA0
  "Target Terror - Bonus 1",             // 0xA1
  "Bramble Scramble - Bonus 1",           // 0xA2
  "Windy Well - Bonus 2",                // 0xA3
  "Web Woods - Bonus 1",                 // 0xA4
  "Toxic Tower - Bonus 1",               // 0xA5
  "Bramble Blast - Bonus 1",             // 0xA6
  "Screech's Sprint - Bonus 1",          // 0xA7
  "Gangplank Galley - Bonus 1",          // 0xA8
  "Squawks's Shaft - Bonus 3",           // 0xA9
  "Kannon's Klaim - Bonus 3",            // 0xAA
  "Kannon's Klaim - Bonus 1",            // 0xAB
  "Squawks's Shaft - Bonus 1",           // 0xAC
  "Kannon's Klaim - Bonus 2",            // 0xAD
  "Hornet Hole - Bonus 1",               // 0xAE
  "Parrot Chute Panic - Bonus 2",        // 0xAF

  // 0xB0 - 0xBF: More bonuses + special
  "Hornet Hole - Bonus 3",               // 0xB0
  "Parrot Chute Panic - Bonus 1",        // 0xB1
  "Rambi Rumble - Bonus 2",              // 0xB2
  "Hornet Hole - Bonus 2",               // 0xB3
  "Rambi Rumble - Bonus 1",              // 0xB4
  "Chain Link Chamber - Bonus 1",        // 0xB5
  "Chain Link Chamber - Bonus 2",        // 0xB6
  "Castle Crush - Bonus 1",              // 0xB7
  "Castle Crush - Bonus 2",              // 0xB8
  "Stronghold Showdown",                   // 0xB9 (Boss - W5)
  "Squawks's Shaft - Bonus 2",           // 0xBA
  "Web Woods - Bonus 2",                 // 0xBB
  "Windy Well - Bonus 1",               // 0xBC
  "Haunted Hall - Bonus 1",              // 0xBD
  "Rickety Race - End",                   // 0xBE
  "Haunted Hall - End",                    // 0xBF
];

// Verify count
console.log(`Total entries: ${LEVEL_NAMES.length}`); // Should be 192
console.log(`Null entries: ${LEVEL_NAMES.filter(x => x === null).length}`);
