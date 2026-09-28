"""Command-line interface for Nomi."""

import argparse


def non_empty_name(value: str) -> str:
    """Reject empty or whitespace-only names passed to the CLI."""
    if not value.strip():
        raise argparse.ArgumentTypeError("name must not be empty")
    return value


def build_parser() -> argparse.ArgumentParser:
    """Build the Nomi command-line parser."""
    parser = argparse.ArgumentParser(prog="nomi", description="Nomi command-line tools.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    greet = subcommands.add_parser("greet", help="Greet someone by name.")
    greet.add_argument("name", type=non_empty_name, help="Name of the person to greet.")
    greet.set_defaults(handler=greet_command)

    return parser


def greet_command(name: str) -> None:
    """Print a friendly greeting."""
    print(f"Hello, {name}!")


def main() -> None:
    args = build_parser().parse_args()
    args.handler(args.name)


if __name__ == "__main__":
    main()
