# Boundary picture

From `94cdf5f15f31` to the working tree. Source: xv boundary (ast and regex). Generated; check it against the diff.

## Shape hints

- none

## Modules

- touched: scripts/agentcli, scripts/orders, scripts/prototypes, scripts/run
- added: none
- removed: none
- now calling out of the process: none

## Edges

- added: none
- removed: none

```mermaid
flowchart LR
  m0["evals/grade"]
  m1["evals/report"]
  m2["evals/run"]
  m3["scripts/adapt"]
  m4["scripts/agentcli"]
  m5["scripts/boundary"]
  m6["scripts/check"]
  m7["scripts/install"]
  m8["scripts/listen"]
  m9["scripts/orders"]
  m10["scripts/packet"]
  m11["scripts/playwright_agents"]
  m12["scripts/promote"]
  m13["scripts/prompt"]
  m14["scripts/prototypes"]
  m15["scripts/record"]
  m16["scripts/recording"]
  m17["scripts/retro"]
  m18["scripts/run"]
  m19["scripts/spend"]
  m20["scripts/wall"]
  m21["scripts/xvlib"]
  m0 --> m4
  m0 --> m8
  m0 --> m15
  m0 --> m21
  m1 --> m19
  m2 --> m0
  m2 --> m4
  m2 --> m19
  m2 --> m21
  m3 --> m6
  m3 --> m21
  m4 --> m21
  m5 --> m21
  m6 --> m7
  m6 --> m21
  m7 --> m21
  m8 --> m4
  m8 --> m13
  m8 --> m18
  m8 --> m21
  m9 --> m19
  m9 --> m21
  m10 --> m21
  m11 --> m21
  m12 --> m6
  m12 --> m21
  m13 --> m4
  m13 --> m15
  m13 --> m21
  m14 --> m4
  m14 --> m9
  m14 --> m13
  m14 --> m15
  m14 --> m19
  m14 --> m21
  m15 --> m19
  m15 --> m21
  m16 --> m21
  m17 --> m4
  m17 --> m12
  m17 --> m13
  m17 --> m19
  m17 --> m21
  m18 --> m4
  m18 --> m5
  m18 --> m9
  m18 --> m10
  m18 --> m13
  m18 --> m14
  m18 --> m15
  m18 --> m17
  m18 --> m19
  m18 --> m20
  m18 --> m21
  m19 --> m21
  m20 --> m21
```

## Tables

- added: none
- removed: none

## Surface paths

- added: none
- removed: none

<details><summary>JSON</summary>

```json
{
 "base": "94cdf5f15f31c53d02fc8de787ce85889627e799",
 "touched": [
  "scripts/agentcli",
  "scripts/orders",
  "scripts/prototypes",
  "scripts/run"
 ],
 "modules_added": [],
 "modules_removed": [],
 "edges_added": [],
 "edges_removed": [],
 "outbound_added": [],
 "tables": {
  "added": [],
  "removed": []
 },
 "surfaces": {
  "added": [],
  "removed": []
 },
 "after": {
  "modules": [
   "evals/grade",
   "evals/report",
   "evals/run",
   "scripts/adapt",
   "scripts/agentcli",
   "scripts/boundary",
   "scripts/check",
   "scripts/install",
   "scripts/listen",
   "scripts/orders",
   "scripts/packet",
   "scripts/playwright_agents",
   "scripts/promote",
   "scripts/prompt",
   "scripts/prototypes",
   "scripts/record",
   "scripts/recording",
   "scripts/retro",
   "scripts/run",
   "scripts/spend",
   "scripts/wall",
   "scripts/xvlib"
  ],
  "edges": [
   [
    "evals/grade",
    "scripts/agentcli"
   ],
   [
    "evals/grade",
    "scripts/listen"
   ],
   [
    "evals/grade",
    "scripts/record"
   ],
   [
    "evals/grade",
    "scripts/xvlib"
   ],
   [
    "evals/report",
    "scripts/spend"
   ],
   [
    "evals/run",
    "evals/grade"
   ],
   [
    "evals/run",
    "scripts/agentcli"
   ],
   [
    "evals/run",
    "scripts/spend"
   ],
   [
    "evals/run",
    "scripts/xvlib"
   ],
   [
    "scripts/adapt",
    "scripts/check"
   ],
   [
    "scripts/adapt",
    "scripts/xvlib"
   ],
   [
    "scripts/agentcli",
    "scripts/xvlib"
   ],
   [
    "scripts/boundary",
    "scripts/xvlib"
   ],
   [
    "scripts/check",
    "scripts/install"
   ],
   [
    "scripts/check",
    "scripts/xvlib"
   ],
   [
    "scripts/install",
    "scripts/xvlib"
   ],
   [
    "scripts/listen",
    "scripts/agentcli"
   ],
   [
    "scripts/listen",
    "scripts/prompt"
   ],
   [
    "scripts/listen",
    "scripts/run"
   ],
   [
    "scripts/listen",
    "scripts/xvlib"
   ],
   [
    "scripts/orders",
    "scripts/spend"
   ],
   [
    "scripts/orders",
    "scripts/xvlib"
   ],
   [
    "scripts/packet",
    "scripts/xvlib"
   ],
   [
    "scripts/playwright_agents",
    "scripts/xvlib"
   ],
   [
    "scripts/promote",
    "scripts/check"
   ],
   [
    "scripts/promote",
    "scripts/xvlib"
   ],
   [
    "scripts/prompt",
    "scripts/agentcli"
   ],
   [
    "scripts/prompt",
    "scripts/record"
   ],
   [
    "scripts/prompt",
    "scripts/xvlib"
   ],
   [
    "scripts/prototypes",
    "scripts/agentcli"
   ],
   [
    "scripts/prototypes",
    "scripts/orders"
   ],
   [
    "scripts/prototypes",
    "scripts/prompt"
   ],
   [
    "scripts/prototypes",
    "scripts/record"
   ],
   [
    "scripts/prototypes",
    "scripts/spend"
   ],
   [
    "scripts/prototypes",
    "scripts/xvlib"
   ],
   [
    "scripts/record",
    "scripts/spend"
   ],
   [
    "scripts/record",
    "scripts/xvlib"
   ],
   [
    "scripts/recording",
    "scripts/xvlib"
   ],
   [
    "scripts/retro",
    "scripts/agentcli"
   ],
   [
    "scripts/retro",
    "scripts/promote"
   ],
   [
    "scripts/retro",
    "scripts/prompt"
   ],
   [
    "scripts/retro",
    "scripts/spend"
   ],
   [
    "scripts/retro",
    "scripts/xvlib"
   ],
   [
    "scripts/run",
    "scripts/agentcli"
   ],
   [
    "scripts/run",
    "scripts/boundary"
   ],
   [
    "scripts/run",
    "scripts/orders"
   ],
   [
    "scripts/run",
    "scripts/packet"
   ],
   [
    "scripts/run",
    "scripts/prompt"
   ],
   [
    "scripts/run",
    "scripts/prototypes"
   ],
   [
    "scripts/run",
    "scripts/record"
   ],
   [
    "scripts/run",
    "scripts/retro"
   ],
   [
    "scripts/run",
    "scripts/spend"
   ],
   [
    "scripts/run",
    "scripts/wall"
   ],
   [
    "scripts/run",
    "scripts/xvlib"
   ],
   [
    "scripts/spend",
    "scripts/xvlib"
   ],
   [
    "scripts/wall",
    "scripts/xvlib"
   ]
  ],
  "outbound": [
   "evals/grade",
   "scripts/boundary",
   "scripts/check",
   "scripts/listen",
   "scripts/recording"
  ]
 },
 "source": "xv boundary (ast and regex)",
 "shape_hints": []
}
```
</details>
