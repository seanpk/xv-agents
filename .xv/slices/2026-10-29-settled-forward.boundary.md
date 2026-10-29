# Boundary picture

From `cafedce2750c` to the working tree. Source: xv boundary (ast and regex). Generated; check it against the diff.

## Shape hints

- none

## Modules

- touched: scripts/record
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
  m7["scripts/decisions"]
  m8["scripts/install"]
  m9["scripts/listen"]
  m10["scripts/orders"]
  m11["scripts/packet"]
  m12["scripts/playwright_agents"]
  m13["scripts/promote"]
  m14["scripts/prompt"]
  m15["scripts/prototypes"]
  m16["scripts/record"]
  m17["scripts/recording"]
  m18["scripts/retro"]
  m19["scripts/run"]
  m20["scripts/spend"]
  m21["scripts/wall"]
  m22["scripts/xvlib"]
  m0 --> m4
  m0 --> m9
  m0 --> m16
  m0 --> m22
  m1 --> m20
  m2 --> m0
  m2 --> m4
  m2 --> m20
  m2 --> m22
  m3 --> m6
  m3 --> m22
  m4 --> m22
  m5 --> m22
  m6 --> m8
  m6 --> m22
  m7 --> m18
  m7 --> m22
  m8 --> m22
  m9 --> m4
  m9 --> m14
  m9 --> m19
  m9 --> m22
  m10 --> m20
  m10 --> m22
  m11 --> m22
  m12 --> m22
  m13 --> m6
  m13 --> m22
  m14 --> m4
  m14 --> m16
  m14 --> m22
  m15 --> m4
  m15 --> m10
  m15 --> m14
  m15 --> m16
  m15 --> m20
  m15 --> m22
  m16 --> m20
  m16 --> m22
  m17 --> m22
  m18 --> m4
  m18 --> m13
  m18 --> m14
  m18 --> m20
  m18 --> m22
  m19 --> m4
  m19 --> m5
  m19 --> m10
  m19 --> m11
  m19 --> m14
  m19 --> m15
  m19 --> m16
  m19 --> m18
  m19 --> m20
  m19 --> m21
  m19 --> m22
  m20 --> m22
  m21 --> m22
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
 "base": "cafedce2750c9b8bfed996553f0f139df2563608",
 "touched": [
  "scripts/record"
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
   "scripts/decisions",
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
    "scripts/decisions",
    "scripts/retro"
   ],
   [
    "scripts/decisions",
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
