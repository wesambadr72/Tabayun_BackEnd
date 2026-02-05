from ai_processor import compare_laws


def main() -> None:
    saudi = "نص القانون السعودي التجريبي."
    foreign = "نص القانون الأجنبي التجريبي."
    summary = compare_laws(saudi, foreign, foreign_country="Germany")
    print(summary)


if __name__ == "__main__":
    main()

