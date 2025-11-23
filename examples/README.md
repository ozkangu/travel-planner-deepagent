# Examples Directory

This directory contains example scripts demonstrating different implementations.

## V1 Examples (DeepAgent-based)

### `v1_demo.py`
Basic demonstration of V1 (DeepAgent) architecture.

**Run:**
```bash
python examples/v1_demo.py
```

**Features:**
- Simple mode: Pre-defined queries
- Interactive mode: Chat interface
- Tools mode: Direct tool testing

### `v1_monitored.py`
V1 demo with full monitoring and metrics.

**Run:**
```bash
python examples/v1_monitored.py
```

**Features:**
- Token usage tracking
- Cost estimation
- LangSmith integration
- Performance metrics

### `v1_examples.py`
Collection of V1 usage examples.

**Run:**
```bash
python examples/v1_examples.py
```

## V2 Examples (LangGraph-based) ⭐ Recommended

### `v2_examples.py`
Comprehensive V2 examples demonstrating LangGraph architecture.

**Run:**
```bash
python examples/v2_examples.py
```

**Examples included:**
1. Full trip planning
2. Flight search only
3. Hotel search only
4. Weather check
5. Activity search
6. Custom preferences

## 📊 Comparison

| Aspect | V1 Examples | V2 Examples |
|--------|-------------|-------------|
| Speed | Slower (~20s) | Faster (~4s) |
| Cost | Higher ($0.126) | Lower ($0.021) |
| Complexity | More complex | Simpler |
| Recommended | For reference | **For production** |

## 🚀 Quick Start

**Try V2 first:**
```bash
python examples/v2_examples.py
```

**Compare with V1:**
```bash
python examples/v1_demo.py
```

## 📚 More Resources

- [V2 Quick Start](../docs/QUICKSTART_V2.md)
- [V1 vs V2 Comparison](../docs/V1_VS_V2_COMPARISON.md)
- [Main README](../README.md)
