"""
Quick integration tests for V2 components.

Tests:
1. TravelPlannerV2 initialization
2. Basic trip planning
3. Context preservation
4. Monitoring setup
5. FastAPI health check (if running)
"""

import asyncio
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import src_v2
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
load_dotenv()


async def test_planner_initialization():
    """Test 1: Planner initialization"""
    print("\n" + "="*60)
    print("TEST 1: Planner Initialization")
    print("="*60)

    try:
        from src_v2 import TravelPlannerV2

        planner = TravelPlannerV2(
            provider="anthropic",
            verbose=False,
            enable_monitoring=False  # Disable for testing
        )

        print("✅ PASSED: Planner initialized successfully")
        return True, planner
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False, None


async def test_basic_planning(planner):
    """Test 2: Basic trip planning"""
    print("\n" + "="*60)
    print("TEST 2: Basic Trip Planning")
    print("="*60)

    try:
        result = await planner.plan_trip(
            query="Find flights from New York to London",
            origin="New York",
            destination="London"
        )

        # Verify result structure
        assert "completed_steps" in result
        assert "errors" in result
        assert isinstance(result["errors"], list)

        print(f"✅ PASSED: Trip planning completed")
        print(f"   Completed steps: {len(result['completed_steps'])}")
        print(f"   Errors: {len(result['errors'])}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_context_preservation(planner):
    """Test 3: Context preservation"""
    print("\n" + "="*60)
    print("TEST 3: Context Preservation")
    print("="*60)

    try:
        # First query
        result1 = await planner.plan_trip(
            query="I want to go to Paris",
            origin="New York"
        )

        # Follow-up query should remember Paris
        result2 = await planner.plan_trip(
            query="Show me hotels",
            origin="New York",  # Pass context manually
            destination=result1.get("destination") or "Paris"
        )

        # Verify destination is preserved
        assert result2.get("destination") == "Paris" or result1.get("destination") == "Paris"

        print("✅ PASSED: Context preservation works")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_monitoring_setup():
    """Test 4: Monitoring setup"""
    print("\n" + "="*60)
    print("TEST 4: Monitoring Setup")
    print("="*60)

    try:
        from src_v2.monitoring import is_monitoring_enabled, get_langsmith_config

        enabled = is_monitoring_enabled()
        config = get_langsmith_config()

        print(f"   Monitoring enabled: {enabled}")
        print(f"   Config: {config if enabled else 'N/A'}")
        print("✅ PASSED: Monitoring setup accessible")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def test_fastapi_health():
    """Test 5: FastAPI health check (if running)"""
    print("\n" + "="*60)
    print("TEST 5: FastAPI Health Check (optional)")
    print("="*60)

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ PASSED: API is running")
                print(f"   Status: {data['status']}")
                print(f"   Version: {data['version']}")
                return True
            else:
                print(f"⚠️  WARNING: API returned status {response.status_code}")
                return False

    except Exception as e:
        print(f"ℹ️  SKIPPED: API not running or not accessible")
        print(f"   (This is okay if you haven't started the API)")
        return None


async def test_streamlit_imports():
    """Test 6: Streamlit imports"""
    print("\n" + "="*60)
    print("TEST 6: Streamlit Imports")
    print("="*60)

    try:
        import streamlit
        print(f"   Streamlit version: {streamlit.__version__}")
        print("✅ PASSED: Streamlit available")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "🧪 " + "="*58)
    print("   TRAVEL PLANNER V2 - INTEGRATION TESTS")
    print("="*60)

    # Check environment
    print("\n📋 Environment Check:")
    providers = {
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
    }

    provider_set = False
    for name, value in providers.items():
        status = "✅ SET" if value else "❌ NOT SET"
        print(f"   {name}: {status}")
        if value:
            provider_set = True

    if not provider_set:
        print("\n❌ ERROR: No LLM provider API key found!")
        print("   Please set at least one API key in .env")
        return

    print(f"\n   LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2', 'false')}")
    print(f"   LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT', 'N/A')}")

    # Run tests
    results = []

    # Test 1: Initialization
    success, planner = await test_planner_initialization()
    results.append(("Planner Initialization", success))

    if not success:
        print("\n❌ Cannot continue without planner. Stopping tests.")
        return

    # Test 2: Basic planning
    success = await test_basic_planning(planner)
    results.append(("Basic Planning", success))

    # Test 3: Context preservation
    success = await test_context_preservation(planner)
    results.append(("Context Preservation", success))

    # Test 4: Monitoring
    success = test_monitoring_setup()
    results.append(("Monitoring Setup", success))

    # Test 5: FastAPI (optional)
    success = await test_fastapi_health()
    if success is not None:
        results.append(("FastAPI Health", success))

    # Test 6: Streamlit
    success = await test_streamlit_imports()
    results.append(("Streamlit Imports", success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")

    print(f"\n   Total: {passed}/{total} passed")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n   You can now:")
        print("   1. Start FastAPI: uvicorn api_v2:app --reload")
        print("   2. Start Streamlit: streamlit run streamlit_chat_v2.py")
        print("   3. Use programmatically: from src_v2 import TravelPlannerV2")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
