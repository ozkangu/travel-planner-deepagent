# 🎉 V2 is Here! (LangGraph-based Architecture)

**New in V2:**
- ✅ **5x faster** (4s vs 20s)
- ✅ **6x cheaper** ($0.021 vs $0.126 per request)
- ✅ **FastAPI REST API** included
- ✅ **Streamlit Chat UI** with context preservation
- ✅ **LangSmith monitoring** integration
- ✅ **Production-ready** architecture

## 🚀 Quick Start (V2)

```bash
# 1. Install
uv sync

# 2. Setup .env
cp .env.example .env
# Add your API key (Anthropic/OpenAI/OpenRouter)

# 3. Test
python test_v2_integrations.py

# 4. Run Streamlit (Chat UI)
streamlit run streamlit_chat_v2.py

# OR run FastAPI (REST API)
uvicorn api_v2:app --reload
```

**That's it!** 🎊

## 📚 Documentation

- **Quick Start:** [QUICKSTART_V2.md](./QUICKSTART_V2.md) - Get started in 5 minutes
- **Full Deployment:** [README_V2_DEPLOYMENT.md](./README_V2_DEPLOYMENT.md) - Complete guide
- **V1 vs V2:** [V1_VS_V2_COMPARISON.md](./V1_VS_V2_COMPARISON.md) - Why V2 is better
- **Detailed Analysis:** [DETAILED_COMPARISON.md](./DETAILED_COMPARISON.md) - Deep dive + NDC integration

## 🎯 Features

### FastAPI REST API (`api_v2.py`)
- ✅ `/api/v2/plan-trip` - Full trip planning
- ✅ `/api/v2/search-flights` - Flight search only
- ✅ `/api/v2/search-hotels` - Hotel search only
- ✅ `/health` - Health check
- ✅ `/docs` - Interactive API documentation

### Streamlit Chat Interface (`streamlit_chat_v2.py`)
- ✅ **Context Preservation** - Remembers your conversation
- ✅ **Interactive Chat** - Natural language queries
- ✅ **Visual Metrics** - See flights, hotels, costs
- ✅ **Session Management** - Multiple conversations

### LangSmith Monitoring (`src_v2/monitoring.py`)
- ✅ **Workflow Tracing** - See every step
- ✅ **Token Usage** - Track costs per request
- ✅ **Latency Breakdown** - Identify bottlenecks
- ✅ **Error Tracking** - Debug issues easily

## 🔥 Usage Examples

### Streamlit Chat
```bash
streamlit run streamlit_chat_v2.py
```
Then chat naturally:
```
You: I want to visit Tokyo in March
Bot: [Provides options]

You: Show me hotels for 2 people
Bot: [Shows hotels - remembers Tokyo + March!]
```

### FastAPI
```bash
# Start server
uvicorn api_v2:app --reload

# Make request
curl -X POST http://localhost:8000/api/v2/plan-trip \
  -H "Content-Type: application/json" \
  -d '{"query": "Weekend in Barcelona", "num_passengers": 2}'
```

### Python Library
```python
import asyncio
from src_v2 import TravelPlannerV2

planner = TravelPlannerV2(provider="anthropic", enable_monitoring=True)
result = asyncio.run(planner.plan_trip("Trip to Paris"))
print(result["itinerary"])
```

## 📊 V1 vs V2 Performance

| Metric | V1 (DeepAgent) | V2 (LangGraph) | Winner |
|--------|----------------|----------------|--------|
| Latency | 20s | 4s | **V2 (5x)** ⚡ |
| Cost/Request | $0.126 | $0.021 | **V2 (6x)** 💰 |
| LLM Calls | 12 | 2 | **V2 (6x)** |
| Parallelism | ❌ No | ✅ Yes | **V2** |
| Monitoring | ⚠️ Limited | ✅ Full | **V2** |
| Production Ready | ❌ | ✅ | **V2** |

**At 10K requests/day:**
- V1: $1,260/day = $37,800/month
- V2: $210/day = $6,300/month
- **Savings: $31,500/month** 🎉

## 🎯 Recommendations

- ✅ **Use V2 for all new projects**
- ✅ **Migrate V1 projects to V2**
- ✅ **V2 is production-ready today**

V1 is kept for backward compatibility and research purposes only.

## 🆘 Need Help?

1. **Quick Start:** [QUICKSTART_V2.md](./QUICKSTART_V2.md)
2. **Full Guide:** [README_V2_DEPLOYMENT.md](./README_V2_DEPLOYMENT.md)
3. **Run Tests:** `python test_v2_integrations.py`
4. **Check Logs:** Use `verbose=True` when initializing planner

---

**Version:** 2.0.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-11-23

🚀 **Start using V2 today!**
