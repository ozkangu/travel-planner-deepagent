# Tests Directory

Integration tests for Travel Planner.

## Test Files

### `test_v2_integrations.py`
Comprehensive integration tests for V2 (LangGraph) implementation.

**Run:**
```bash
python tests/test_v2_integrations.py
```

**Tests included:**
1. ✅ Planner initialization
2. ✅ Basic trip planning
3. ✅ Context preservation
4. ✅ Monitoring setup
5. ✅ FastAPI health check (optional)
6. ✅ Streamlit imports

**Expected output:**
```
🎉 ALL TESTS PASSED! 🎉

   You can now:
   1. Start FastAPI: uvicorn api_v2:app --reload
   2. Start Streamlit: streamlit run streamlit_chat_v2.py
   3. Use programmatically: from src_v2 import TravelPlannerV2
```

## Running Tests

### Quick Test
```bash
python tests/test_v2_integrations.py
```

### With Verbose Output
```bash
python tests/test_v2_integrations.py 2>&1 | tee test_output.log
```

### Check Specific Test
```python
# Run in Python
import asyncio
from src_v2 import TravelPlannerV2

async def quick_test():
    planner = TravelPlannerV2(provider="anthropic", verbose=False)
    result = await planner.plan_trip("Test trip to Paris")
    print("✅ Test passed!" if result else "❌ Test failed!")

asyncio.run(quick_test())
```

## Test Requirements

**Environment variables required:**
```bash
# At least one API key
ANTHROPIC_API_KEY=sk-ant-...
# OR
OPENAI_API_KEY=sk-...
# OR
OPENROUTER_API_KEY=sk-or-...
```

**Optional (for monitoring tests):**
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
```

## Troubleshooting

### Test Failures

**Issue: "No API key found"**
```bash
# Solution: Check .env file
cp .env.example .env
# Edit .env and add your API key
```

**Issue: "Planner not initialized"**
```bash
# Solution: Verify dependencies
uv sync
```

**Issue: "FastAPI test skipped"**
```bash
# This is normal if API is not running
# To test API, start it first:
uvicorn api_v2:app --reload &
python tests/test_v2_integrations.py
pkill -f uvicorn
```

## Adding New Tests

To add tests, edit `test_v2_integrations.py`:

```python
async def test_your_feature(planner):
    """Test your new feature"""
    try:
        result = await planner.your_method()
        assert result is not None
        print("✅ PASSED: Your feature works")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
```

## CI/CD Integration

For CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: python tests/test_v2_integrations.py
```

## 📚 More Resources

- [V2 Documentation](../docs/DEPLOYMENT.md)
- [Main README](../README.md)
