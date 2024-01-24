def escape_markdown(text):
    # Список специальных символов Markdown, которые нужно экранировать
    markdown_chars = ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!"]
    # Экранирование каждого символа
    for char in markdown_chars:
        text = text.replace(char, "\\" + char)
    return text