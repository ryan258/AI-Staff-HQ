# Workflow: Strategy to Tech Handoff

**Goal:** Translate high-level strategic requirements into executable technical specifications without losing fidelity.

**Participants:**
- **Coordinator:** Chief of Staff
- **Source:** Software Architect (Strategic View) or Product Manager
- **Destination:** Automation Specialist / Toolmaker

## The Problem
Strategic plans often lack the technical rigor needed for implementation, while technical specs often miss the "why" behind the "what." This workflow bridges that gap.

## The Workflow

### Phase 1: Strategic Definition (Source)
**Standard:** Must produce a "functional requirements" list, not just "user stories."

**Prompt Pattern:**
> "Acting as the Software Architect, review this feature request: [Insert Request]. Decompose it into a set of 'Functional Requirements' and 'Non-Functional Requirements'. Do not write code yet. Focus on data flow, user constraints, and system boundaries."

### Phase 2: The Bridge (Coordination)
**Standard:** The Chief of Staff validates clarity before passing to Tech.

**Prompt Pattern:**
> "Acting as the Chief of Staff, review these requirements for ambiguity. Are there any edge cases defined? Any missing error states? If yes, ask the Software Architect to clarify. If no, approve for Handoff."

### Phase 3: Technical Specification (Destination)
**Standard:** Converts requirements into a "Implementation Plan" or code.

**Prompt Pattern:**
> "Acting as the Automation Specialist, take these approved Functional Requirements and draft a Python script (or system architecture) to satisfy them. Include inline comments explaining how each requirement is met."

## Example Transcript

**User:** "We need a script to scrape our competitors' pricing."

**Software Architect:** "Here are the requirements: 1. Respect robots.txt. 2. handle rate limiting. 3. Output to CSV. 4. Run daily..."

**Chief of Staff:** "Approved. Handoff to Automation Specialist."

**Automation Specialist:** *[Generates `scrape_pricing.py` with `time.sleep()` for rate limiting and `robots` parser]*
