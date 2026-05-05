# sloth-vdf-solver

Python solver for the Sloth VDF (Verifiable Delay Function) challenge used by some WAFs.

When a WAF returns a `429` with a proof-of-work challenge, this solver extracts the parameters, computes the proof, and gives you the valid cookie.

## How it works

The WAF embeds a JS challenge in the 429 response:

```js
var args = {prime: "ab3f...", input: "8d2c...", t: 2000, time: 1711..., ip: "..."};
```

The solver computes `t` iterations of `y = y^((p+1)/4) mod p` (modular square root in a Blum prime field), then builds the cookie from the result.

## Usage

### From the command line

```bash
python solver.py response_429.html
# wafsc_vdf_sloth=1711...|1.2.3.4|2000|a8f3...
```

### In your code

```python
from solver import solve_challenge

# html = the body of a 429 response
cookie_value = solve_challenge(html)
# Set cookie "wafsc_vdf_sloth" = cookie_value and retry your request
```

### Step by step

```python
from solver import parse_challenge, solve_vdf, build_cookie

args = parse_challenge(html_429)
proof = solve_vdf(args)
cookie = build_cookie(args, proof)
```

## Dependencies

Pure Python, no required dependencies.

For a ~10x speedup on the typical 4096-bit prime used by these WAFs, install [`gmpy2`](https://pypi.org/project/gmpy2/) — the solver picks it up automatically:

```bash
pip install gmpy2
```

Benchmark on the rebuy.de challenge (4096-bit prime, t=200):

| Backend       | Time   |
|---------------|--------|
| Python `pow`  | ~39 s  |
| `gmpy2.powmod`| ~3.4 s |

You can verify which backend is active with `solver.HAS_GMPY2`.
