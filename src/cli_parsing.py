def parse_int(name: str, value: object, min_value: int, max_value: int,
              *unexpected: object, **unexpected_kwargs: object) -> None:
    if unexpected or unexpected_kwargs:
        extra = list(unexpected) + [f"--{k}" for k in unexpected_kwargs]
        print("[ERROR] Unexpected extra argument(s): "
              f"{extra}\n")
        raise SystemExit
    try:
        if isinstance(value, bool):
            raise ValueError
        if isinstance(value, float):
            raise ValueError
        int_size = int(value)  # type: ignore[call-overload]

    except ValueError:
        raise ValueError(f"[ERROR] {name} must be an integer value "
                         f"between {min_value} and {max_value}.")
    if not min_value < int_size <= max_value:
        raise ValueError(f"[ERROR] {name} must be an integer value "
                         f"between {min_value} and {max_value}.")
    if name == "max_chunk_size" and int_size < min_value:
        raise ValueError(
            f"[WARNING] {name}={int_size} is very small: "
            f"Invalid minimum chunk size: the value must be at least "
            f"{min_value} characters. "
            "Smaller chunks are not suitable for reliable embedding "
            "generation and may result in poor RAG retrieval performance.")
