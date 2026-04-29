# CursorRIPER

**页面ID:** 2815376544  
**URL:** https://confluence.shopee.io/pages/viewpage.action?pageId=2815376544

## GitHub链接
https://github.com/johnpeterman72/CursorRIPER/tree/main

## Overview

CursorRIPER provides a systematic approach to software development through five distinct operational modes:

1. **Research**: Information gathering and understanding existing code
2. **Innovate**: Brainstorming potential approaches and solutions
3. **Plan**: Creating detailed technical specifications
4. **Execute**: Implementing approved plans with precision
5. **Review**: Validating implementation against plans

This framework prevents unintended modifications while maintaining perfect continuity across coding sessions.

```mermaid
flowchart TD
Start([Start]) --> Init{Project<br>Initialized?}
Init -->|No| StartPhase[START Phase]
Init -->|Yes| RIPER[RIPER Workflow]
subgraph StartPhase[START Phase]
S1[Requirements] --> S2[Technology]
S2 --> S3[Architecture]
S3 --> S4[Scaffolding]
S4 --> S5[Environment]
S5 --> S6[Memory Bank]
end
subgraph RIPER[RIPER Workflow]
R[Research] --> I[Innovate]
I --> P[Plan]
P --> E[Execute]
E --> Rev[Review]
Rev -.-> R
end
StartPhase --> RIPER
```

## Features

* **Structured Workflow**: Clear separation of development phases
* **Memory Bank**: Persistent documentation across sessions
* **Project Intelligence**: Learning from patterns and preferences
* **State Management**: Explicit tracking of project phase and mode
* **Safe Initialization**: Guided setup with protection against re-initialization

## Getting Started

1. Copy the framework files to your project and change the extension to .mdc:

   ```
   cp -r /path/to/CursorRIPER/src/.cursor/* .cursor/
   rename 's/\.md$/.mdc/' *.md
   ```
2. Initialize your project with:

   ```
   /start
   ```
3. Follow the START phase to set up your project structure and memory bank
4. Use the RIPER workflow for ongoing development