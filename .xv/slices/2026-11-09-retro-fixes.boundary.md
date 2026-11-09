# Boundary picture

From `4f6dcb707076` to the working tree. Source: xv boundary (ast and regex). Generated; check it against the diff.

## Shape hints

- none

## Modules

- touched: scripts/run, scripts/wall
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
  m11["scripts/names"]
  m12["scripts/orders"]
  m13["scripts/packet"]
  m14["scripts/playwright_agents"]
  m15["scripts/promote"]
  m16["scripts/prompt"]
  m17["scripts/prototypes"]
  m18["scripts/record"]
  m19["scripts/recording"]
  m20["scripts/retro"]
  m21["scripts/run"]
  m22["scripts/spend"]
  m23["scripts/suite"]
  m24["scripts/wall"]
  m25["scripts/xvlib"]
  m0 --> m4
  m0 --> m9
  m0 --> m18
  m0 --> m25
  m1 --> m22
  m2 --> m0
  m2 --> m4
  m2 --> m22
  m2 --> m25
  m3 --> m6
  m3 --> m25
  m4 --> m25
  m5 --> m25
  m6 --> m8
  m6 --> m25
  m7 --> m20
  m7 --> m25
  m8 --> m25
  m9 --> m4
  m9 --> m16
  m9 --> m21
  m9 --> m25
  m10 --> m24
  m10 --> m25
  m12 --> m22
  m12 --> m25
  m13 --> m25
  m14 --> m25
  m15 --> m6
  m15 --> m25
  m16 --> m4
  m16 --> m18
  m16 --> m25
  m17 --> m4
  m17 --> m12
  m17 --> m16
  m17 --> m18
  m17 --> m22
  m17 --> m25
  m18 --> m10
  m18 --> m11
  m18 --> m12
  m18 --> m13
  m18 --> m22
  m18 --> m23
  m18 --> m24
  m18 --> m25
  m19 --> m25
  m20 --> m4
  m20 --> m15
  m20 --> m16
  m20 --> m22
  m20 --> m25
  m21 --> m4
  m21 --> m5
  m21 --> m11
  m21 --> m12
  m21 --> m13
  m21 --> m16
  m21 --> m17
  m21 --> m18
  m21 --> m20
  m21 --> m22
  m21 --> m23
  m21 --> m24
  m21 --> m25
  m22 --> m25
  m23 --> m25
  m24 --> m25
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
 "base": "4f6dcb707076f9b7a130b27302e6cafdd92e73e1",
 "touched": [
  "scripts/run",
  "scripts/wall"
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
   "scripts/moves",
   "scripts/names",
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
   "scripts/suite",
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
    "scripts/moves"
   ],
   [
    "scripts/record",
    "scripts/names"
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
    "scripts/suite"
   ],
   [
    "scripts/record",
    "scripts/wall"
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
    "scripts/names"
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
    "scripts/suite"
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
    "scripts/suite",
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
