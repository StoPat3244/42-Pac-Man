import sys


def main() -> None:
    try:
        from src.cli import CLI
        import fire
        fire.Fire(CLI)
    except SystemExit as e:
        if e.code != 0:
            print("Run 'uv run python3 -m src' for usage "
                  "informations.")
            sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
