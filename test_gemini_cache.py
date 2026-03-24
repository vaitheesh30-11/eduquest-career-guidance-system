from utils.gemini_client import GeminiClient
import utils.gemini_client as gemini_client_module


class MockResponse:
    def __init__(self, text: str):
        self.text = text
        self.usage_metadata = {
            "prompt_token_count": 10,
            "candidates_token_count": 5,
            "total_token_count": 15,
        }


class CountingProvider:
    def __init__(self):
        self.call_count = 0

    def generate_content(self, prompt, generation_config=None):
        self.call_count += 1
        return MockResponse(f"mock-response-for:{prompt}")


class JsonCountingProvider:
    def __init__(self):
        self.call_count = 0

    def generate_content(self, prompt, generation_config=None):
        self.call_count += 1
        return MockResponse('{"value":"cached","status":"ok"}')


class CountingGeminiClient(GeminiClient):
    def __init__(self, provider):
        self.model = "mock-model"
        self.api_keys = ["mock-key"]
        self.current_key_index = 0
        self.client = provider
        self.model_instance = provider.generate_content
        self.is_initialized = True
        self.last_error = None
        self._session_metrics = self._new_session_metrics()


def test_generate_content_uses_cache_for_identical_requests():
    original_is_new_api = gemini_client_module.is_new_api
    original_genai_module = gemini_client_module.genai_module
    gemini_client_module.is_new_api = False
    gemini_client_module.genai_module = "mock-sdk"
    GeminiClient._response_cache.clear()
    GeminiClient._structured_response_cache.clear()

    provider = CountingProvider()
    client = CountingGeminiClient(provider)

    first = client.generate_content("hello", temperature=0.2, max_tokens=100)
    second = client.generate_content("hello", temperature=0.2, max_tokens=100)

    metrics = client.get_session_metrics()

    assert first == second
    assert provider.call_count == 1
    assert metrics["llm_calls"] == 2
    assert metrics["successful_calls"] == 2
    assert metrics["cache_hits"] == 1
    assert metrics["cache_misses"] == 1
    assert metrics["calls"][0]["cache_hit"] is False
    assert metrics["calls"][1]["cache_hit"] is True
    assert metrics["response_cache"]["hits"] >= 1

    GeminiClient._response_cache.clear()
    GeminiClient._structured_response_cache.clear()
    gemini_client_module.is_new_api = original_is_new_api
    gemini_client_module.genai_module = original_genai_module


def test_generate_structured_json_uses_structured_cache_for_identical_requests():
    original_is_new_api = gemini_client_module.is_new_api
    original_genai_module = gemini_client_module.genai_module
    gemini_client_module.is_new_api = False
    gemini_client_module.genai_module = "mock-sdk"
    GeminiClient._response_cache.clear()
    GeminiClient._structured_response_cache.clear()

    provider = JsonCountingProvider()
    client = CountingGeminiClient(provider)

    first = client.generate_structured_json(
        "json please",
        required_fields=["value", "status"],
        temperature=0.2,
        max_tokens=100,
        trace_metadata={"agent_name": "TestAgent"},
    )
    second = client.generate_structured_json(
        "json please",
        required_fields=["value", "status"],
        temperature=0.2,
        max_tokens=100,
        trace_metadata={"agent_name": "TestAgent"},
    )

    metrics = client.get_session_metrics()

    assert first == second
    assert provider.call_count == 1
    assert metrics["structured_cache_hits"] == 1
    assert metrics["structured_cache_misses"] == 1
    assert metrics["structured_cache_hit_rate"] == 0.5
    assert metrics["structured_cache"]["hits"] >= 1

    GeminiClient._response_cache.clear()
    GeminiClient._structured_response_cache.clear()
    gemini_client_module.is_new_api = original_is_new_api
    gemini_client_module.genai_module = original_genai_module
