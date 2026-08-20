"""Command-line entry point for the HAND-MOUSE desktop companion."""

from __future__ import annotations

import argparse
import asyncio
import secrets

from .server import CompanionConfig, CompanionServer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HAND-MOUSE desktop companion")
    parser.add_argument("--host", default="127.0.0.1", help="bind address; non-loopback hosts require TLS")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token", help="authentication token; generated if omitted")
    parser.add_argument("--origin", help="allowed browser Origin, e.g. https://your-site.netlify.app")
    parser.add_argument("--certfile", help="PEM TLS certificate for non-loopback connections")
    parser.add_argument("--keyfile", help="PEM private key for non-loopback connections")
    args = parser.parse_args()

    token = args.token or secrets.token_urlsafe(32)
    print("HAND-MOUSE companion token:")
    print(token)
    print("Keep this token private.")

    config = CompanionConfig(
        host=args.host,
        port=args.port,
        token=token,
        origin=args.origin,
        certfile=args.certfile,
        keyfile=args.keyfile,
    )
    try:
        asyncio.run(CompanionServer(config).run())
    except KeyboardInterrupt:
        print("\nHAND-MOUSE companion stopped.")


if __name__ == "__main__":
    main()
