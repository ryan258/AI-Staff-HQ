# Model Control in AI Staff HQ Swarm

## Overview

AI Staff HQ supports multiple ways to control which models are used by specialists.
The default model is configured in `.env` (currently `nvidia/nemotron-3-super-120b-a12b:free`). Examples below show optional overrides.

## Model Control Hierarchy

Models are selected in this priority order:

1. **Direct Override** (highest priority)
2. **Budget Mode** (explicit force-all setting)
3. **Role-Based Routing** (from config file)
4. **Department Routing** (from config file)
5. **Default Model** (from .env)

---

## 1. Direct Override (Runtime)

### Via SwarmRunner

```python
from orchestrator.swarm_runner import SwarmRunner

runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-sonnet-5.5",  # All agents use this
    temperature=0.7,
)
```

### Via the Flagship CLI

```bash
# Override model for all specialists
uv run workflows/planning_swarm.py "Write a tagline" \
    --model "anthropic/claude-sonnet-5.5"

# With temperature
uv run workflows/planning_swarm.py "Write a tagline" \
    --model "anthropic/claude-sonnet-5.5" \
    --temperature 0.9
```

### Via Test Script

```python
runner = SwarmRunner(
    staff_dir,
    config=config,
    model_override="anthropic/claude-opus-5.5",  # Override
    auto_approve=True,
)
```

---

## 2. Budget Mode (Cheap Override)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
budget_mode:
  enabled: true
  model: "nvidia/nemotron-3-super-120b-a12b:free" # Free/cheap model
```

When enabled, ALL specialists use the budget model (overrides everything except direct override).

---

## 3. Role-Based Routing (Config File)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
role_routing:
  # Chief of Staff gets the best model
  "Strategic Coordinator & Project Orchestrator": "anthropic/claude-opus-5.5"

  # Copywriters get creative models
  "Conversion Copy & Brand Messaging Specialist": "anthropic/claude-sonnet-5.5"

  # Analysts get reasoning models
  "Market Research & Competitive Intelligence Specialist": "openai/gpt-6.1-sol"
```

**Note**: Use the full role name from the specialist's YAML `core_identity.role` field.

---

## 4. Department-Based Routing (Config File)

Edit `ai-staff-hq/config/model_routing.yaml`:

```yaml
department_routing:
  strategy: "anthropic/claude-opus-5.5" # Best reasoning
  producers: "anthropic/claude-sonnet-5.5" # Creative writing
  commerce: "anthropic/claude-sonnet-5.5" # Marketing
  tech: "openai/gpt-6.1-sol" # Technical reasoning
  health-lifestyle: "anthropic/claude-sonnet-5.5"
  knowledge: "anthropic/claude-opus-5.5" # Expert knowledge
```

**Departments**:

- `strategy` - Market analysis, research, planning
- `producers` - Content creation, narrative, design
- `commerce` - SEO, marketing, growth
- `tech` - Software, automation, infrastructure
- `health-lifestyle` - Wellness, habits, meditation
- `knowledge` - Legal, financial, tax

---

## 5. Default Model (.env)

Set default in `ai-staff-hq/.env`:

```bash
# Default model for all specialists
DEFAULT_MODEL="nvidia/nemotron-3-super-120b-a12b:free"

# OpenRouter API key
OPENROUTER_API_KEY="your-key-here"
```

---

## Popular Model Choices

### Best Quality (Expensive)

```yaml
anthropic/claude-opus-5.5        # Strongest reasoning and orchestration
openai/gpt-6.1-sol-pro           # Deep reasoning
```

### Balanced (Recommended)

```yaml
anthropic/claude-sonnet-5.5      # Great quality/price
openai/gpt-6.1-sol               # Fast and capable
google/gemini-4-argon            # Long context, good value
```

### Budget (Cheap/Free)

```yaml
nvidia/nemotron-3-super-120b-a12b:free  # Free default; tools + structured output
google/gemma-4-31b-it:free              # Free
anthropic/claude-haiku-5.5              # Cheapest Anthropic
```

Free models are retired without notice. Check `https://openrouter.ai/api/v1/models`
and keep `fallback_models` in `config/model_routing.yaml` pointed at live IDs.

---

## Example: Mixed Strategy

`config/model_routing.yaml`:

```yaml
# Best models for critical roles
role_routing:
  "Strategic Coordinator & Project Orchestrator": "anthropic/claude-opus-5.5"
  "Conversion Copy & Brand Messaging Specialist": "anthropic/claude-sonnet-5.5"

# Departments use balanced models
department_routing:
  strategy: "anthropic/claude-sonnet-5.5"
  producers: "anthropic/claude-sonnet-5.5"
  commerce: "anthropic/claude-sonnet-5.5"
  tech: "anthropic/claude-sonnet-5.5"
  health-lifestyle: "anthropic/claude-haiku-5.5" # Cheaper for wellness
  knowledge: "anthropic/claude-opus-5.5" # Expensive for legal/tax

# Budget mode disabled (use real models)
budget_mode:
  enabled: false
```

---

## Cost Optimization Strategies

### 1. Hybrid Approach

- Chief of Staff: `claude-opus-5.5` (planning & synthesis)
- Task execution: `claude-sonnet-5.5` (balance)
- Simple tasks: `claude-haiku-5.5` (cheap)

### 2. Budget Mode for Development

```yaml
budget_mode:
  enabled: true
  model: "nvidia/nemotron-3-super-120b-a12b:free"
```

### 3. Override During Testing

```python
# Use cheap model for testing
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-haiku-5.5",
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

- `anthropic/claude-opus-5.5`
- `anthropic/claude-sonnet-5.5`
- `anthropic/claude-haiku-5.5`
- `openai/gpt-6.1-sol`
- `openai/gpt-6.1-sol-pro`
- `google/gemini-4-argon`

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
    model_override="anthropic/claude-sonnet-5.5",  # HERE
)
```

---

## Quick Start

**For testing (cheap)**:

```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-haiku-5.5",
)
```

**For production (balanced)**:

```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-sonnet-5.5",
)
```

**For best quality (expensive)**:

```python
runner = SwarmRunner(
    staff_dir,
    model_override="anthropic/claude-opus-5.5",
)
```

**No override (use config file)**:

```python
runner = SwarmRunner(staff_dir)  # Uses model_routing.yaml
```
