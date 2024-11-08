def escape_markdown(text: str) -> str:
    markdown_special_chars = r"_*[]()"
    for char in markdown_special_chars:
        text = text.replace(char, f"\\{char}")
    return text
