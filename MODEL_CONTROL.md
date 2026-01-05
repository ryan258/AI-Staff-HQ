# Model Control in AI Staff HQ Swarm

## Overview

AI Staff HQ supports multiple ways to control which models are used by specialists.

## Model Control Hierarchy

Models are selected in this priority order:

1. **Direct Override** (highest priority)
2. **Role-Based Routing** (from config file)
3. **Department Routing** (from config file)
4. **Default Model** (from .env)
5. **Budget Mode** (fallback)

---

## 1. Direct Override (Runtime)

### Via SwarmRunner

```python
from orchestrator.swarm_runner import SwarmRunner

runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-3.5-sonnet",  # All agents use this
    temperature=0.7,
)
```

### Via CLI Wrapper

```bash
# Override model for all specialists
python bin/dhp-swarm-content.py "Write a tagline" \
    --model "anthropic/claude-3.5-sonnet"

# With temperature
python bin/dhp-swarm-content.py "Write a tagline" \
    --model "anthropic/claude-3.5-sonnet" \
    --temperature 0.9
```

### Via Test Script

```python
runner = SwarmRunner(
    staff_dir,
    config=config,
    model_override="anthropic/claude-opus-4",  # Override
    auto_approve=True,
)
```

---

## 2. Role-Based Routing (Config File)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
role_routing:
  # Chief of Staff gets the best model
  "Strategic Coordinator & Project Orchestrator": "anthropic/claude-opus-4"

  # Copywriters get creative models
  "Conversion Copy & Brand Messaging Specialist": "anthropic/claude-3.5-sonnet"

  # Analysts get reasoning models
  "Market Research & Competitive Intelligence Specialist": "openai/o1-mini"
```

**Note**: Use the full role name from the specialist's YAML `core_identity.role` field.

---

## 3. Department-Based Routing (Config File)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
department_routing:
  strategy: "anthropic/claude-opus-4"      # Best reasoning
  producers: "anthropic/claude-3.5-sonnet" # Creative writing
  commerce: "anthropic/claude-3.5-sonnet"  # Marketing
  tech: "openai/o1-mini"                   # Technical reasoning
  health-lifestyle: "anthropic/claude-3.5-sonnet"
  knowledge: "anthropic/claude-opus-4"     # Expert knowledge
```

**Departments**:
- `strategy` - Market analysis, research, planning
- `producers` - Content creation, narrative, design
- `commerce` - SEO, marketing, growth
- `tech` - Software, automation, infrastructure
- `health-lifestyle` - Wellness, habits, meditation
- `knowledge` - Legal, financial, tax

---

## 4. Default Model (.env)

Set default in `ai-staff-hq/.env`:

```bash
# Default model for all specialists
DEFAULT_MODEL="anthropic/claude-3.5-sonnet"

# OpenRouter API key
OPENROUTER_API_KEY="your-key-here"
```

---

## 5. Budget Mode (Cheap Fallback)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
budget_mode:
  enabled: true
  model: "google/gemini-flash-1.5"  # Free/cheap model
```

When enabled, ALL specialists use the budget model (overrides everything except direct override).

---

## Popular Model Choices

### Best Quality (Expensive)
```yaml
anthropic/claude-opus-4         # Best overall
openai/o1                        # Best reasoning
anthropic/claude-3.7-sonnet      # Latest Sonnet
```

### Balanced (Recommended)
```yaml
anthropic/claude-3.5-sonnet      # Great quality/price
openai/gpt-4o                    # Fast and capable
google/gemini-pro-1.5            # Good value
```

### Budget (Cheap/Free)
```yaml
google/gemini-flash-1.5          # Free
anthropic/claude-3-haiku         # Cheapest Anthropic
openai/gpt-4o-mini               # Cheap OpenAI
```

---

## Example: Mixed Strategy

`config/model_routing.yaml`:

```yaml
# Best models for critical roles
role_routing:
  "Strategic Coordinator & Project Orchestrator": "anthropic/claude-opus-4"
  "Conversion Copy & Brand Messaging Specialist": "anthropic/claude-3.5-sonnet"

# Departments use balanced models
department_routing:
  strategy: "anthropic/claude-3.5-sonnet"
  producers: "anthropic/claude-3.5-sonnet"
  commerce: "anthropic/claude-3.5-sonnet"
  tech: "anthropic/claude-3.5-sonnet"
  health-lifestyle: "anthropic/claude-3-haiku"  # Cheaper for wellness
  knowledge: "anthropic/claude-opus-4"          # Expensive for legal/tax

# Budget mode disabled (use real models)
budget_mode:
  enabled: false
```

---

## Cost Optimization Strategies

### 1. Hybrid Approach
- Chief of Staff: `claude-opus-4` (planning & synthesis)
- Task execution: `claude-3.5-sonnet` (balance)
- Simple tasks: `claude-3-haiku` (cheap)

### 2. Budget Mode for Development
```yaml
budget_mode:
  enabled: true
  model: "google/gemini-flash-1.5"
```

### 3. Override During Testing
```python
# Use cheap model for testing
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-3-haiku",
    config=config,
)
```

---

## Checking Current Configuration

```python
from tools.engine.llm import ModelRouter

router = ModelRouter()
print("Current routing config:")
print(router.config)
```

Or check the file directly:
```bash
cat ai-staff-hq/config/model_routing.yaml
```

---

## Model Format

Use OpenRouter model names:

- `anthropic/claude-opus-4`
- `anthropic/claude-3.5-sonnet`
- `anthropic/claude-3-haiku`
- `openai/gpt-4o`
- `openai/o1`
- `google/gemini-pro-1.5`

See full list: https://openrouter.ai/models

---

## SwarmConfig Model Control

```python
from workflows.schemas.swarm import SwarmConfig

# No built-in model control in SwarmConfig (use SwarmRunner)
config = SwarmConfig(
    max_parallel=5,
    enable_parallel=True,
    # Models controlled via SwarmRunner, not SwarmConfig
)

runner = SwarmRunner(
    staff_dir,
    config=config,
    model_override="anthropic/claude-3.5-sonnet",  # HERE
)
```

---

## Quick Start

**For testing (cheap)**:
```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-3-haiku",
)
```

**For production (balanced)**:
```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-3.5-sonnet",
)
```

**For best quality (expensive)**:
```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-opus-4",
)
```

**No override (use config file)**:
```python
runner = SwarmRunner(staff_dir)  # Uses model_routing.yaml
```
