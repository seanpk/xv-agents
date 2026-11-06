# Boundary picture

From `5d5e75fc7a73` to the working tree. Source: xv boundary (ast and regex). Generated; check it against the diff.

## Shape hints

- a surface path was added or removed

## Modules

- touched: scripts/orders, scripts/prompt, scripts/record, scripts/run
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
  m10["scripts/moves"]
  m11["scripts/orders"]
  m12["scripts/packet"]
  m13["scripts/playwright_agents"]
  m14["scripts/promote"]
  m15["scripts/prompt"]
  m16["scripts/prototypes"]
  m17["scripts/record"]
  m18["scripts/recording"]
  m19["scripts/retro"]
  m20["scripts/run"]
  m21["scripts/spend"]
  m22["scripts/wall"]
  m23["scripts/xvlib"]
  m0 --> m4
  m0 --> m9
  m0 --> m17
  m0 --> m23
  m1 --> m21
  m2 --> m0
  m2 --> m4
  m2 --> m21
  m2 --> m23
  m3 --> m6
  m3 --> m23
  m4 --> m23
  m5 --> m23
  m6 --> m8
  m6 --> m23
  m7 --> m19
  m7 --> m23
  m8 --> m23
  m9 --> m4
  m9 --> m15
  m9 --> m20
  m9 --> m23
  m10 --> m22
  m10 --> m23
  m11 --> m21
  m11 --> m23
  m12 --> m23
  m13 --> m23
  m14 --> m6
  m14 --> m23
  m15 --> m4
  m15 --> m17
  m15 --> m23
  m16 --> m4
  m16 --> m11
  m16 --> m15
  m16 --> m17
  m16 --> m21
  m16 --> m23
  m17 --> m11
  m17 --> m12
  m17 --> m21
  m17 --> m23
  m18 --> m23
  m19 --> m4
  m19 --> m14
  m19 --> m15
  m19 --> m21
  m19 --> m23
  m20 --> m4
  m20 --> m5
  m20 --> m10
  m20 --> m11
  m20 --> m12
  m20 --> m15
  m20 --> m16
  m20 --> m17
  m20 --> m19
  m20 --> m21
  m20 --> m22
  m20 --> m23
  m21 --> m23
  m22 --> m23
```

## Tables

- added: none
- removed: none

## Surface paths

- added: /red
- removed: none

<details><summary>JSON</summary>

```json
{
 "base": "5d5e75fc7a7371d74a3884cfbae919785adbb4e7",
 "touched": [
  "scripts/orders",
  "scripts/prompt",
  "scripts/record",
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
  "added": [
   "/red"
  ],
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
   "scripts/moves",
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
    "scripts/moves",
    "scripts/wall"
   ],
   [
    "scripts/moves",
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
    "scripts/orders"
   ],
   [
    "scripts/record",
    "scripts/packet"
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
    "scripts/moves"
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
 "shape_hints": [
  "a surface path was added or removed"
 ]
}
```
</details>
