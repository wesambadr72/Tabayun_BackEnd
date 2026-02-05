from ai_processor import simplify_text


def main() -> None:
    sample_text = "نص قانوني تجريبي."
    result = simplify_text(sample_text)
    print(result)


if __name__ == "__main__":
    main()

