from ai_processor import simplify_text, compare_laws, RAGChatbot


def main() -> None:
    original_text = "نص قانوني تجريبي."
    simplified = simplify_text(original_text)
    summary = compare_laws(simplified, simplified, foreign_country="Germany")
    bot = RAGChatbot()
    answer = bot.answer("ما هو ملخص هذا القانون؟")
    print(simplified)
    print(summary)
    print(answer)


if __name__ == "__main__":
    main()

