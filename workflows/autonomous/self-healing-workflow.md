# 🤖 Self-Healing Autonomous Workflow

> An autonomous workflow for identifying and proposing solutions to performance gaps within the AI-Staff-HQ.

## 🎯 Workflow Overview

**Purpose**: To automatically diagnose and propose solutions for specialist KPI failures, closing the loop on performance optimization.  
**Trigger**: A "NOT MET" verdict from the Actuary in a `retrospective-template.md`.  
**Facilitation**: This is an autonomous workflow, primarily driven by the Productivity Architect.  
**Deliverables**: A proposed programmatic change to a specialist's YAML file, presented for user approval.

---

## 🔄 Workflow Steps

### **Phase 1: Trigger and Data Ingestion**

1.  **Trigger**: The workflow is initiated by the `SELF-HEALING WORKFLOW ACTIVATION (AUTONOMOUS)` section in the `retrospective-template.md`.
2.  **Data Ingestion**: The Productivity Architect receives a data payload containing:
    - The name of the specialist who failed the KPI.
    - The specific KPI that was not met.
    - A link to the log file of the retrospective.
    - The project brief and other relevant context.

### **Phase 2: Analysis and Diagnosis (Productivity Architect)**

1.  **Contextual Analysis**: The Productivity Architect reviews the retrospective log to understand the full context of the project and the KPI failure.
2.  **Specialist Analysis**: The Productivity Architect reads the YAML file of the specialist in question to understand their current configuration.
3.  **Root Cause Analysis**: The Productivity Architect analyzes the specialist's skills, activation patterns, and quality standards to identify the likely root cause of the performance gap.

### **Phase 3: Solution Proposal (Productivity Architect)**

1.  **Propose Change**: Based on the root cause analysis, the Productivity Architect formulates a precise, programmatic change to the specialist's YAML file.
2.  **Document Proposal**: The proposed change is documented in a new file at `temp/proposed_change.md` in a clear "before-and-after" format.

### **Phase 4: User Approval**

1.  **Present Proposal**: The `temp/proposed_change.md` file is presented to the user for approval.
2.  **User Decision**: The user can either approve or reject the proposed change.

### **Phase 5: Implementation (Toolmaker)**

1.  **Trigger Implementation**: If the user approves the change, the Toolmaker is activated.
2.  **Apply Change**: The Toolmaker reads the `temp/proposed_change.md` file and uses the `replace` tool to apply the change to the relevant specialist's YAML file.
3.  **Cleanup**: The `temp/proposed_change.md` file is deleted.

### **Phase 6: Workflow Completion**

1.  **Documentation**: The retrospective log is updated with the outcome of the self-healing workflow.
2.  **Notification**: The user is notified that the specialist has been updated.