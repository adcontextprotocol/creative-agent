# Creative Agent Testing Principles

## Test to the Spec, NOT to the Code

**Write tests as if you have zero knowledge of the implementation.**

### The Problem

Tests that validate code output against code output catch nothing.

Example that missed production bugs:
```python
# ❌ WRONG - Test written by looking at code
def test_list_formats():
    result = list_creative_formats()
    assert "formats" in result  # Passes even with bugs!
```

### The Solution

**Read the ADCP spec first. Use generated Pydantic schemas. Validate every response.**

```python
# ✅ CORRECT - Test written by reading spec
def test_list_formats():
    from schemas_generated import ListCreativeFormatsResponse

    result_json = list_creative_formats()
    result = json.loads(result_json)  # Catches double-encoding
    ListCreativeFormatsResponse.model_validate(result)  # Validates ALL fields
```

### Process for Every Test

1. **Read spec/schema FIRST** - Never look at implementation
2. **Import generated Pydantic model** - From `schemas_generated/`
3. **Call tool as client would** - Test public API, get JSON string
4. **Parse JSON once** - `json.loads(result)` catches encoding bugs
5. **Validate with Pydantic** - `.model_validate()` catches all schema violations

### What This Catches

- **Double-encoding**: `'{"result": "{...}"}'` → `json.loads()` fails or wrong structure
- **Missing required fields**: Pydantic raises ValidationError
- **Wrong field types**: Pydantic raises ValidationError
- **Extra fields not in spec**: Pydantic raises ValidationError (when `extra="forbid"`)
- **Invalid values**: Constraints like `ge=0`, `pattern=...` enforced

### Example: Bugs Found

Real bugs caught by spec-first testing that code-first tests missed:

1. **Missing `preview_id`** - Required per spec, not returned
2. **Missing `renders` array** - Required per spec, not returned
3. **Extra `adcp_version`** - Not in spec, added by mistake

Old test EXPECTED the bug:
```python
def test_preview():
    result = json.loads(preview_creative(...))
    assert "adcp_version" in result  # Test validates the bug!
```

New test CAUGHT the bug:
```python
def test_preview():
    result = json.loads(preview_creative(...))
    PreviewCreativeResponse.model_validate(result)  # ValidationError: extra field!
```

### Never

- ❌ Look at code before writing test
- ❌ Compare output to output: `assert result == expected_from_code`
- ❌ Trust variable names or comments
- ❌ Test internal types instead of wire format
- ❌ Mock everything (hides serialization bugs)

### Always

- ✅ Read spec first
- ✅ Use generated Pydantic schemas
- ✅ Call public API (tools/endpoints)
- ✅ Parse JSON explicitly
- ✅ Validate with `.model_validate()`
- ✅ Test error cases per spec

### For Protocol Implementations (MCP, ADCP, A2A)

Every response must:
1. Be valid JSON (single parse, no double-encoding)
2. Match published schema exactly (Pydantic validates)
3. Have no extra fields (unless spec allows)
4. Have all required fields (Pydantic enforces)
5. Use correct types (Pydantic enforces)

**If your test would pass with broken code, it's not a good test.**
