"""
Sloth VDF (Verifiable Delay Function) solver.

Solves the proof-of-work challenge used by WAFs based on the Sloth VDF scheme.
Given a challenge {prime, input, t}, computes t iterations of modular square roots
and returns the proof cookie.
"""

import re
import json


def solve_vdf(args: dict) -> str:
    """
    Solve a Sloth VDF challenge.

    Computes t iterations of y = y^((p+1)/4) mod p (modular square root
    in a Blum prime field).

    Args:
        args: Challenge parameters with keys: prime (hex), input (hex), t (int)

    Returns:
        Proof as a hex string.
    """
    prime = int(args["prime"], 16)
    inp = int(args["input"], 16)
    t = args["t"]
    exp = (prime + 1) // 4

    # Normalize to quadratic residue
    y = inp % prime
    if y != 0:
        if pow(y, (prime - 1) // 2, prime) != 1:
            y = prime - y

    # Iterate
    for _ in range(t):
        y = pow(y, exp, prime)

    return hex(y)[2:]


def parse_challenge(html: str) -> dict | None:
    """
    Extract VDF challenge args from a 429 HTML response.

    Looks for: var args = {prime: "...", input: "...", t: ..., time: ..., ip: "..."};

    Returns:
        Dict with challenge parameters, or None if not found.
    """
    match = re.search(r'var\s+args\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))


def build_cookie(args: dict, proof_hex: str) -> str:
    """Build the wafsc_vdf_sloth cookie from challenge args and proof."""
    return f"{args['time']}|{args['ip']}|{args['t']}|{proof_hex}"


def solve_challenge(html: str) -> str | None:
    """
    One-shot: parse a 429 response and return the solved cookie value.

    Args:
        html: The full HTML body of the 429 response.

    Returns:
        The cookie value string, or None if parsing failed.
    """
    args = parse_challenge(html)
    if not args:
        return None
    proof = solve_vdf(args)
    return build_cookie(args, proof)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            html = f.read()
        cookie = solve_challenge(html)
        if cookie:
            print(f"wafsc_vdf_sloth={cookie}")
        else:
            print("No challenge found in input.")
    else:
        print("Usage: python solver.py <429_response.html>")
        print("       Parses the VDF challenge and prints the solved cookie.")
