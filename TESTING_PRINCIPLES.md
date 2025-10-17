# Testing Principles - Test to the Spec, NOT to the Code

## The Problem

**Tests that validate code output against code output catch nothing.**

Real example from production:
```python
# Server returns (WRONG):
'{"result": "{\"formats\": [...]}"}'  # Double-encoded JSON

# Test that MISSED it:
def test_list_formats():
    result = list_creative_formats()
    assert "formats" in result  # ✓ Passes! But response is invalid
```

The test passed because it only checked if the string contained "formats" - it never validated the actual response structure against the spec.

## The Solution: Test to the Spec

**Write every test as if you have ZERO knowledge of the implementation.**

### Step-by-Step Process

1. **Read the spec/schema FIRST** - Don't look at code
2. **Understand the contract** - What MUST the API return?
3. **Use generated Pydantic schemas** - They ARE the spec
4. **Test the public interface** - Call it like a real client would
5. **Validate against schema** - Parse and validate EVERY response

### Example: Testing list_creative_formats

```python
# ❌ WRONG - Testing to the code
def test_list_formats():
    result = list_creative_formats()
    # Just checks it runs - catches nothing
    assert result is not None

# ❌ WRONG - Comparing to code output
def test_list_formats():
    result = list_creative_formats()
    expected = json.dumps({"formats": [...]})  # Copied from code
    assert result == expected  # Brittle and validates nothing

# ✅ CORRECT - Testing to the spec
def test_list_formats_returns_valid_adcp_response():
    """Test that list_creative_formats returns valid ListCreativeFormatsResponse per ADCP spec."""
    from creative_agent.schemas_generated._schemas_v1_creative_list_creative_formats_response_json import (
        ListCreativeFormatsResponse,
    )

    # 1. Call as a client would (string response)
    result_json = list_creative_formats()

    # 2. Parse as JSON (catches double-encoding)
    result_dict = json.loads(result_json)

    # 3. Validate against ADCP schema (catches schema violations)
    response = ListCreativeFormatsResponse.model_validate(result_dict)

    # 4. Verify ADCP spec requirements
    assert response.formats is not None, "formats field is required per ADCP spec"
    assert len(response.formats) > 0, "must return at least one format"
    assert response.creative_agents is not None, "creative_agents field is required"

    # 5. Verify format structure per spec
    for fmt in response.formats:
        assert fmt.format_id is not None
        assert fmt.format_id.id is not None
        assert fmt.format_id.agent_url is not None
```

### Why This Works

The double-encoding bug above would be caught at step 2:
```python
# Server returns: '{"result": "{\"formats\": [...]}"}'
result_dict = json.loads(result_json)  # → {"result": "..."}
ListCreativeFormatsResponse.model_validate(result_dict)  # → ValidationError: field 'formats' required
```

## Rules for Protocol Testing (MCP, ADCP, A2A)

### 1. Always Test Wire Format

```python
# ❌ WRONG - Testing internal types
def test_preview():
    result = preview_creative(...)  # Returns PreviewResponse object
    assert isinstance(result, PreviewResponse)  # Meaningless

# ✅ CORRECT - Testing serialized format
def test_preview():
    result_json = preview_creative(...)  # Returns JSON string
    result_dict = json.loads(result_json)  # Parse like a client
    PreviewCreativeResponse.model_validate(result_dict)  # Validate per spec
```

### 2. Never Trust Variable Names or Comments

```python
# Code says:
creative_manifest = {"formats": [...]}  # ← Variable name lies

# Test discovers:
CreativeManifest.model_validate(creative_manifest)  # ValidationError!
# Actual spec: {"format_id": ..., "assets": {...}}
```

### 3. Test Error Cases Per Spec, Not Per Implementation

```python
# ❌ WRONG - Based on code inspection
def test_errors():
    result = preview_creative(format_id="invalid")
    assert "error" in result  # Vague

# ✅ CORRECT - Based on spec requirements
def test_missing_format_returns_error():
    """Per ADCP spec, unknown format_id MUST return error with description."""
    result_json = preview_creative(format_id="unknown_format_999", ...)
    result = json.loads(result_json)

    assert "error" in result, "ADCP spec requires 'error' field"
    assert isinstance(result["error"], str), "error must be string per spec"
    assert "not found" in result["error"].lower(), "error must describe the problem"
```

### 4. Validate Every Field Type

```python
def test_preview_response_structure():
    """Validate PreviewCreativeResponse matches ADCP schema exactly."""
    result_json = preview_creative(...)
    result = json.loads(result_json)

    # Use Pydantic to validate - it checks EVERYTHING
    response = PreviewCreativeResponse.model_validate(result)

    # Pydantic verified:
    # - All required fields present
    # - All field types correct
    # - All nested objects valid
    # - All enums have valid values
    # - All URLs are valid URLs
    # - All constraints satisfied (ge=0, pattern=..., etc.)
```

## Common Mistakes That Hide Bugs

### 1. Mocking Too Much

```python
# ❌ Mocks hide serialization bugs
@patch('server.generate_preview_html')
def test_preview(mock_gen):
    mock_gen.return_value = "..." # Never tests real function

# ✅ Only mock external dependencies
@patch('storage.upload_to_s3')
def test_preview(mock_s3):
    result = preview_creative(...)  # Tests real serialization path
    response = PreviewCreativeResponse.model_validate(json.loads(result))
```

### 2. Testing Implementation Details

```python
# ❌ Tests internal structure
def test_preview():
    result = preview_creative(...)
    assert result._internal_cache is not None  # Who cares?

# ✅ Tests public contract
def test_preview():
    result_json = preview_creative(...)
    response = PreviewCreativeResponse.model_validate_json(result_json)
    assert response.previews is not None  # Per spec
```

### 3. Assuming Serialization Works

```python
# ❌ Never validates JSON
def test_build():
    manifest = build_creative(...)
    assert manifest.format_id == "display_300x250"  # Object access works

# ✅ Validates wire format
def test_build():
    result_json = build_creative(...)
    result = json.loads(result_json)  # Catches encoding bugs
    BuildCreativeResponse.model_validate(result)  # Validates schema
```

## Checklist for Every Test

- [ ] I read the spec/schema before writing the test
- [ ] I use generated Pydantic models from schemas
- [ ] I test the function's public interface (JSON in, JSON out)
- [ ] I call `json.loads()` on string responses
- [ ] I call `.model_validate()` or `.model_validate_json()` on results
- [ ] I verify spec requirements, not code behavior
- [ ] I test error cases as defined in spec
- [ ] I never assume serialization is correct

## Remember

**If your test would pass with a broken implementation, it's not a good test.**

Example:
```python
# Broken code:
def list_formats():
    return json.dumps({"result": json.dumps({"formats": []})})  # Double-encoded!

# Bad test - passes with broken code:
def test_list():
    result = list_formats()
    assert "formats" in result  # ✓ String contains "formats"

# Good test - fails with broken code:
def test_list():
    result_dict = json.loads(list_formats())  # {"result": "..."}
    ListCreativeFormatsResponse.model_validate(result_dict)  # ✗ ValidationError!
```
