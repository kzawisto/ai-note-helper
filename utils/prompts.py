def get_tasks():
      return [
            ("Summarize", 0),
            ("Bibtex", 1),
            ("Fix Grammar", 2),
            ("Paraphrase", 3),
            ("Explain", 4),
            ("Analyze", 5),
            ("Translate", 6),
            ("Simplify", 7),
            ("Highlight", 8),
        ]


def get_task_prompts():
    """
    Return a list of task prompts for various text processing tasks. Each prompt is designed to guide the language model
    in performing a specific task such as summarizing, composing an email, fixing grammar, extracting keywords, or explaining text.

    :return: List of dictionaries, each containing a 'task' and its corresponding 'prompt'.
    """
    return [
        {
            "task": "Summarize",
            "prompt": """
Summarize the text below:

{text}

Summary:
""".strip(),
        },
        {
            "task": "Bibtex",
            "prompt": """
Format this as Bibtex citation:

{text}

Bibtex:
""".strip(),
        },
        {
            "task": "Fix Grammar",
            "prompt": """
Fix the grammar in the text below:

{text}

Corrected Text:
""".strip(),
        },
        {
            "task": "Paraphrase",
            "prompt": """
Provide 2-3 paraphrases for following text to improve it's 
readability and beauty (please keep original language and length).
If text is in Polish, provide output in Polish, if English, provide output in English.

Here is Text:

{text}

Paraphrases:
""".strip(),
        },
        {
            "task": "Explain",
            "prompt": """
Explain the text below. Please be brief and to the point.

Text:

{text}

Explanation:
""".strip(),
        },
    ]


def get_editor_prompts():
    """
    Return a list of prompts for the text editor task. Each prompt is designed to guide the language model in editing text
    to make it more concise, coherent, and engaging.

    :return: List of dictionaries, each containing an 'editor' and its corresponding 'prompt'.
    """

    # ["Casual", "Formal", "Professional", "Technical", "Simple"]

    return [
        {
            "editor": "Casual",
            "prompt": """
Rewrite the text below in a casual tone:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Formal",
            "prompt": """
Rewrite the text below in a formal tone:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Professional",
            "prompt": """
Rewrite the text below in a professional tone:

{text}

Rewritten Text:
""".strip(),
        },
        {
            "editor": "Technical",
            "prompt": """
Rewrite the text below in a technical tone:

{text}

Rewritten Text:

""".strip(),
        },
        {
            "editor": "Simple",
            "prompt": """
Rewrite the text below in a simple tone:

{text}

Rewritten Text:
""".strip(),
        },
    ]
