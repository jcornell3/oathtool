# OathTool Unit Test Plan

## Executive Summary

This document outlines a comprehensive unit test plan for the oathtool TOTP/HOTP generator library. The plan covers core cryptographic functions, input validation, edge cases, RFC compliance, and integration scenarios.

## Current Test Coverage

### Existing Tests (oathtool/test_oathtool.py)
- ✅ Basic execution with command-line argument
- ✅ Error handling for missing arguments
- ✅ Standalone script generation
- ✅ Piped input from stdin
- ✅ Doctests for `pad()` and `generate_otp()` functions

### Coverage Gaps Identified
- ❌ Direct unit tests for core functions (`hmac`, `clean`, `_one`)
- ❌ Edge cases for cryptographic operations
- ❌ Input validation and sanitization
- ❌ Base32 decoding edge cases
- ❌ Time-based vs counter-based OTP distinction
- ❌ RFC 4226 (HOTP) and RFC 6238 (TOTP) compliance verification
- ❌ Key length variations and security boundaries
- ❌ Error conditions and exception handling
- ❌ Windows executable functionality

---

## Detailed Test Plan

### 1. Core Cryptographic Functions

#### 1.1 `hmac(key, msg)` - HMAC-SHA1 Implementation

**Purpose:** Verify RFC 2104 compliance for HMAC-SHA1

**Test Cases:**

| Test ID | Description | Input | Expected Output | Priority |
|---------|-------------|-------|-----------------|----------|
| HMAC-001 | Standard HMAC with normal key/message | key=b'key', msg=b'message' | Valid SHA1 HMAC (20 bytes) | HIGH |
| HMAC-002 | HMAC with key > 64 bytes (SHA1 block size) | key=b'a'*100, msg=b'test' | Key should be hashed first | HIGH |
| HMAC-003 | HMAC with empty message | key=b'key', msg=b'' | Valid HMAC for empty message | MEDIUM |
| HMAC-004 | HMAC with empty key | key=b'', msg=b'message' | Valid HMAC with padded key | MEDIUM |
| HMAC-005 | HMAC with exactly 64-byte key | key=b'k'*64, msg=b'msg' | Key used directly without padding | LOW |
| HMAC-006 | RFC 2104 test vectors | RFC test cases | Match RFC expected values | HIGH |
| HMAC-007 | Binary message data | key=b'key', msg=b'\x00\xff\xaa' | Handles binary correctly | MEDIUM |

**Implementation Notes:**
- Compare against `hashlib.hmac` for validation
- Verify block size handling (64 bytes for SHA1)
- Test XOR transformations (0x5C and 0x36)

---

#### 1.2 `generate_otp(key, hotp_value)` - OTP Generation

**Purpose:** Verify TOTP/HOTP generation per RFC 6238 and RFC 4226

**Test Cases:**

| Test ID | Description | Input | Expected Output | Priority |
|---------|-------------|-------|-----------------|----------|
| OTP-001 | Known TOTP test vector | key='MZXW6YTBOJUWU23MNU', hotp=52276810 | '487656' | HIGH |
| OTP-002 | Known TOTP test vector (long key) | key='MZXW6YTBOJUWU23MNU'*10, hotp=52276810 | '295635' | HIGH |
| OTP-003 | RFC 6238 test vectors (if available) | RFC test cases | Match RFC values | HIGH |
| OTP-004 | Time-based (no hotp_value) | key='JBSWY3DPEHPK3PXP' | Valid 6-digit code | HIGH |
| OTP-005 | Counter-based (explicit hotp) | key='JBSWY3DPEHPK3PXP', hotp=1 | Deterministic output | HIGH |
| OTP-006 | Same key, different counters | key=same, hotp=[1,2,3] | Different codes | MEDIUM |
| OTP-007 | Same key, same counter | key=same, hotp=same | Identical codes | HIGH |
| OTP-008 | Key with spaces (cleaned) | key='MZXW 6YTB OJUW U23M NU' | Same as cleaned key | MEDIUM |
| OTP-009 | Lowercase base32 key | key='mzxw6ytbojuwu23mnu' | Case-insensitive decode | MEDIUM |
| OTP-010 | Invalid base32 characters | key='INVALID!!!' | Raise appropriate error | HIGH |
| OTP-011 | Empty key | key='' | Raise appropriate error | HIGH |
| OTP-012 | Very short key | key='A' | Valid output or error | MEDIUM |
| OTP-013 | Maximum length key | key='A'*1000 | Handles gracefully | LOW |
| OTP-014 | Truncation algorithm verification | Verify last nibble offset | Correct 31-bit extraction | HIGH |
| OTP-015 | Modulo 1000000 always produces 6 digits | Various inputs | Always 6-digit string | HIGH |
| OTP-016 | Leading zeros preserved | Input produces small number | '000123' format | HIGH |

**Implementation Notes:**
- Verify HOTP counter is big-endian 64-bit (`'>q'`)
- Verify 30-second time step for TOTP
- Verify dynamic truncation per RFC 4226 section 5.3
- Verify 6-digit output with leading zeros

---

#### 1.3 `pad(input, size)` - Base32 Padding

**Purpose:** Verify RFC 3548 base32 padding

**Test Cases:**

| Test ID | Description | Input | Expected Output | Priority |
|---------|-------------|-------|-----------------|----------|
| PAD-001 | Short string (doctest) | 'foo', size=8 | 'foo=====' | HIGH |
| PAD-002 | Needs padding (doctest) | 'MZXW6YTBOJUWU23MNU', size=8 | 'MZXW6YTBOJUWU23MNU======' | HIGH |
| PAD-003 | Already padded | 'MZXW6===', size=8 | 'MZXW6===' (unchanged) | MEDIUM |
| PAD-004 | Exact multiple of size | 'ABCDEFGH', size=8 | 'ABCDEFGH' (no padding) | MEDIUM |
| PAD-005 | Empty string | '', size=8 | '' | LOW |
| PAD-006 | Size 1 | 'AB', size=1 | 'AB' | LOW |
| PAD-007 | Different block sizes | Various sizes | Correct padding amount | MEDIUM |

---

#### 1.4 `clean(input)` - Input Sanitization

**Purpose:** Remove spaces from input keys

**Test Cases:**

| Test ID | Description | Input | Expected Output | Priority |
|---------|-------------|-------|-----------------|----------|
| CLEAN-001 | String with spaces | 'AB CD EF' | 'ABCDEF' | HIGH |
| CLEAN-002 | No spaces | 'ABCDEF' | 'ABCDEF' | MEDIUM |
| CLEAN-003 | Multiple consecutive spaces | 'AB  CD' | 'ABCD' | MEDIUM |
| CLEAN-004 | Leading/trailing spaces | ' ABCD ' | 'ABCD' | MEDIUM |
| CLEAN-005 | Only spaces | '   ' | '' | LOW |
| CLEAN-006 | Empty string | '' | '' | LOW |
| CLEAN-007 | Tabs and newlines | 'AB\tCD\n' | 'AB\tCD\n' (only spaces removed) | MEDIUM |

---

#### 1.5 `_one(items)` - Single Item Extractor

**Purpose:** Ensure exactly one item in collection

**Test Cases:**

| Test ID | Description | Input | Expected Output | Priority |
|---------|-------------|-------|-----------------|----------|
| ONE-001 | Single item list | ['item'] | 'item' | HIGH |
| ONE-002 | Empty list | [] | ValueError | HIGH |
| ONE-003 | Multiple items | ['a', 'b'] | ValueError | HIGH |
| ONE-004 | Tuple with one item | ('item',) | 'item' | MEDIUM |
| ONE-005 | Set with one item | {'item'} | 'item' | LOW |

---

### 2. Input/Output Functions

#### 2.1 `get_key_arg()` - Command-line Argument Parsing

**Test Cases:**

| Test ID | Description | sys.argv | Expected Output | Priority |
|---------|-------------|----------|-----------------|----------|
| ARG-001 | Single argument | ['prog', 'KEY'] | 'KEY' | HIGH |
| ARG-002 | No arguments | ['prog'] | ValueError | HIGH |
| ARG-003 | Multiple arguments | ['prog', 'KEY1', 'KEY2'] | ValueError | HIGH |

---

#### 2.2 `get_key_stdin()` - Stdin Input

**Test Cases:**

| Test ID | Description | Stdin State | Input | Expected Output | Priority |
|---------|-------------|-------------|-------|-----------------|----------|
| STDIN-001 | TTY (interactive) | isatty=True | N/A | False (empty) | HIGH |
| STDIN-002 | Piped input | isatty=False | 'KEY123' | 'KEY123' | HIGH |
| STDIN-003 | Piped with whitespace | isatty=False | '  KEY123\n' | 'KEY123' | HIGH |
| STDIN-004 | Empty piped input | isatty=False | '' | '' | MEDIUM |

---

#### 2.3 `main()` - CLI Entry Point

**Test Cases:**

| Test ID | Description | Input Method | Input | Exit Code | Priority |
|---------|-------------|--------------|-------|-----------|----------|
| MAIN-001 | Valid argument | argv | ['prog', 'KEY'] | 0 | HIGH |
| MAIN-002 | Valid stdin | stdin | 'KEY' | 0 | HIGH |
| MAIN-003 | No input | none | N/A | 1 | HIGH |
| MAIN-004 | Multiple arguments | argv | ['prog', 'K1', 'K2'] | 1 | HIGH |
| MAIN-005 | Stdin priority | both | stdin='K1', argv='K2' | 0 (uses stdin) | MEDIUM |
| MAIN-006 | Invalid key format | argv | ['prog', '!!!'] | Error handling | MEDIUM |

---

### 3. Integration Tests

#### 3.1 End-to-End OTP Generation

**Test Cases:**

| Test ID | Description | Scenario | Expected Result | Priority |
|---------|-------------|----------|-----------------|----------|
| E2E-001 | Google Authenticator compatible | Standard TOTP key | Matches Google Auth | HIGH |
| E2E-002 | Time window validation | Generate at specific time | Correct for 30-sec window | HIGH |
| E2E-003 | Multiple rapid calls | Call twice in same second | Same result | HIGH |
| E2E-004 | Cross-platform compatibility | Same key on different systems | Same result | MEDIUM |

---

#### 3.2 Generate Script Functionality

**Test Cases:**

| Test ID | Description | Scenario | Expected Result | Priority |
|---------|-------------|----------|-----------------|----------|
| SCRIPT-001 | Default location | No target specified | Creates './oathtool' | HIGH |
| SCRIPT-002 | Custom location | Target='/tmp/custom' | Creates at target | HIGH |
| SCRIPT-003 | Script executability | After creation | Script is executable | HIGH |
| SCRIPT-004 | Script functionality | Run generated script | Produces valid OTP | HIGH |
| SCRIPT-005 | Shebang line | Check first line | '#!/usr/bin/env python' | MEDIUM |
| SCRIPT-006 | Path expansion | Target='~/oathtool' | Expands correctly | MEDIUM |

---

### 4. Windows-Specific Tests

#### 4.1 MSIX Package Testing

**Test Cases:**

| Test ID | Description | Scenario | Expected Result | Priority |
|---------|-------------|----------|-----------------|----------|
| WIN-001 | Executable generation | PyInstaller build | Creates oathtool.exe | HIGH |
| WIN-002 | Executable functionality | Run .exe with key | Valid OTP output | HIGH |
| WIN-003 | Executable no-dependency | Run on clean Windows | Works without Python | HIGH |
| WIN-004 | MSIX package creation | Build script execution | Creates .msix file | HIGH |
| WIN-005 | MSIX package installation | Install on Windows 10/11 | Installs successfully | MEDIUM |
| WIN-006 | Command-line arguments | oathtool.exe KEY | Correct behavior | HIGH |
| WIN-007 | Piped input on Windows | echo KEY \| oathtool.exe | Works correctly | MEDIUM |

---

### 5. Security & Edge Cases

#### 5.1 Security Considerations

**Test Cases:**

| Test ID | Description | Scenario | Expected Result | Priority |
|---------|-------------|----------|-----------------|----------|
| SEC-001 | Key not logged | Run with debug output | Key not in logs | HIGH |
| SEC-002 | Memory cleanup | After generation | Sensitive data cleared | LOW |
| SEC-003 | Timing attack resistance | Multiple runs | Consistent timing | LOW |
| SEC-004 | Short key warning | Key < 16 bytes | Warning or error | MEDIUM |

---

#### 5.2 Error Handling

**Test Cases:**

| Test ID | Description | Input | Expected Behavior | Priority |
|---------|-------------|-------|-------------------|----------|
| ERR-001 | Invalid base32 alphabet | Key with '1', '8', '9' | Clear error message | HIGH |
| ERR-002 | Malformed base32 | Incorrect padding | Appropriate exception | HIGH |
| ERR-003 | Unicode input | Key with unicode chars | Handle or reject cleanly | MEDIUM |
| ERR-004 | Very large counter value | hotp > 2^63 | Handle overflow | LOW |
| ERR-005 | Negative counter value | hotp < 0 | Error or handle | LOW |

---

### 6. RFC Compliance Tests

#### 6.1 RFC 4226 (HOTP) Compliance

**Test Cases:**

| Test ID | Description | Test Vector | Expected Result | Priority |
|---------|-------------|-------------|-----------------|----------|
| RFC4226-001 | Test vector 0 | Appendix D values | Match spec | HIGH |
| RFC4226-002 | Test vector 1-9 | Appendix D values | Match spec | HIGH |
| RFC4226-003 | Dynamic truncation | Verify algorithm | Per section 5.3 | HIGH |

---

#### 6.2 RFC 6238 (TOTP) Compliance

**Test Cases:**

| Test ID | Description | Test Vector | Expected Result | Priority |
|---------|-------------|-------------|-----------------|----------|
| RFC6238-001 | SHA1 test vectors | Appendix B values | Match spec | HIGH |
| RFC6238-002 | Time step (T=30) | Verify 30-second windows | Correct steps | HIGH |
| RFC6238-003 | Unix epoch T0=0 | Verify base time | Correct calculation | MEDIUM |

---

## Test Implementation Strategy

### Phase 1: Core Functions (Week 1)
- Implement unit tests for `hmac`, `generate_otp`, `pad`, `clean`, `_one`
- Achieve 100% line coverage for core crypto functions
- Add RFC test vectors

### Phase 2: I/O & Integration (Week 2)
- Implement tests for `main`, `get_key_arg`, `get_key_stdin`
- Add end-to-end integration tests
- Test error conditions and edge cases

### Phase 3: Platform-Specific (Week 3)
- Windows executable tests
- MSIX package tests
- Cross-platform validation

### Phase 4: Security & Compliance (Week 4)
- RFC compliance verification
- Security audit tests
- Performance benchmarking

---

## Test Metrics & Goals

### Coverage Targets
- **Line Coverage:** 100% for core functions
- **Branch Coverage:** 95% overall
- **Integration Coverage:** All public APIs tested

### Quality Gates
- All HIGH priority tests must pass
- No regressions in existing tests
- All RFC compliance tests must pass
- Cross-platform compatibility verified

---

## Test Tools & Framework

### Primary Framework
- **pytest** - Main test runner
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking support

### Additional Tools
- **doctest** - Inline documentation tests (already enabled)
- **hypothesis** - Property-based testing (recommended)
- **tox** - Multi-environment testing (already configured)

### CI/CD Integration
- GitHub Actions (already configured)
- Run on: Windows, macOS, Linux
- Python versions: 3.9, 3.10, 3.11, 3.12, 3.13

---

## Test Data & Fixtures

### Test Fixtures Needed

```python
@pytest.fixture
def valid_test_key():
    return 'JBSWY3DPEHPK3PXP'

@pytest.fixture
def rfc_test_vectors():
    # RFC 4226 Appendix D test vectors
    return {...}

@pytest.fixture
def mock_time():
    # Fixed time for TOTP testing
    return 1234567890

@pytest.fixture
def temp_script(tmp_path):
    # Temporary script location
    return tmp_path / 'oathtool'
```

---

## Acceptance Criteria

### Test Suite Complete When:
1. ✅ All HIGH priority tests implemented and passing
2. ✅ 100% coverage of core cryptographic functions
3. ✅ RFC compliance verified with official test vectors
4. ✅ Cross-platform tests passing (Windows, Linux, macOS)
5. ✅ Windows executable and MSIX tests passing
6. ✅ No security vulnerabilities identified
7. ✅ Documentation updated with test results

---

## Appendix A: Test Data

### Known Good TOTP Keys
```
JBSWY3DPEHPK3PXP - "Hello!"
MZXW6YTBOJUWU23MNU - "foobar"
GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ - "12345678901234567890"
```

### RFC 4226 Test Secret
```
Key: "12345678901234567890" (ASCII)
Base32: GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ
```

---

## Appendix B: References

- [RFC 2104 - HMAC](https://tools.ietf.org/html/rfc2104)
- [RFC 3548 - Base32](https://tools.ietf.org/html/rfc3548)
- [RFC 4226 - HOTP](https://tools.ietf.org/html/rfc4226)
- [RFC 6238 - TOTP](https://tools.ietf.org/html/rfc6238)
- [NIST SP 800-38B - CMAC](https://csrc.nist.gov/publications/detail/sp/800-38b/final)

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-09 | Claude Sonnet 4.5 | Initial comprehensive test plan |

