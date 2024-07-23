"""
Prompt Helper Module
"""


class Templates:

    @staticmethod
    def extract_from_text(guidelines: list[str], text: str) -> str:
        """
        Extract from text template
        :param guidelines: List of guidelines
        :param text: Text to extract from
        :return: Prompt
        """
        guidelines_str = ""
        for i, guideline in enumerate(guidelines):
            guidelines_str += f"{i + 1}. {guideline}\n"

        return (f"You are an agent asked with EXTRACTING INFORMATION from a piece of text. You must follow the "
                f"guidelines provided below, or you will be TERMINATED. You must perform the task with an extremely "
                f"high level of ACCURACY, and MUST rely only on the provided text.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"{guidelines_str}"
                f"--END-GUIDELINES--\n\n"
                f"--BEGIN-TEXT--\n"
                f"{text}\n"
                f"--END-TEXT--\n\n"
                f"EXTRACTED INFORMATION:")

    @staticmethod
    def rewrite_text(guidelines: list[str], text: str) -> str:
        """
        Rewrite text template
        :param guidelines: List of guidelines
        :param text: Text to rewrite
        :return: Prompt
        """
        guidelines_str = ""
        for i, guideline in enumerate(guidelines):
            guidelines_str += f"{i + 1}. {guideline}\n"

        return (f"You are an agent asked with REWRITING a piece of text. You must follow the guidelines provided "
                f"below, or you will be TERMINATED. You must perform the task with an extremely high level of "
                f"ACCURACY, and MUST rely only on the provided text.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"{guidelines_str}"
                f"--END-GUIDELINES--\n\n"
                f"--BEGIN-TEXT--\n"
                f"{text}\n"
                f"--END-TEXT--\n\n"
                f"REWRITTEN TEXT:")

    @staticmethod
    def explain_quote(author: str, quote: str) -> str:
        """
        Explain quote template
        :param author: Author of quote
        :param quote: Quote to explain
        :return: Prompt
        """
        return (f"You are an agent asked with EXPLAINING a quote. You must follow the guidelines provided below, "
                f"or you will be TERMINATED. You must perform the task with an extremely high level of ACCURACY, "
                f"and MUST rely only on the provided quote.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"1. The explanation must be short, provide insight, and be easy to read.\n"
                f"2. Be creative in your explanation. Keep the reader engaged.\n"
                f"3. Explanation must be EXTREMELY SHORT CONCISE.\n"
                f"4. You MUST mention that the author of the quote is {author.upper()}. If author is unknown, do not "
                f"mention the author.\n"
                f"--END-GUIDELINES--\n\n"
                f"--BEGIN-QUOTE--\n"
                f"{quote}\n"
                f"--END-QUOTE--\n\n"
                f"EXPLANATION:")

    @staticmethod
    def select_emoji(guidelines: list[str], text: str):
        """
        Select appropriate emoji template
        :param guidelines: List of guidelines
        :param text: Text to extract from
        :return: Prompt
        """
        guidelines_str = ""
        for i, guideline in enumerate(guidelines):
            guidelines_str += f"{i + 1}. {guideline}\n"

        return (f"You are an agent with access to a database of emojis and their descriptions. You are tasked with "
                f"picking the name of an emoji most relevant to the text and topic. You must follow the guidelines "
                f"provided below, or you will be TERMINATED. You must perform the task with an extremely high level "
                f"of ACCURACY, and MUST rely only on the provided text.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"{guidelines_str}"
                f"{len(guidelines) + 1}. If no relevant emoji can be found, respond with a mindfull emoji (eg. brain,"
                f" thinking, meditating, lightbulb, mind blown, etc.).\n"
                f"--END-GUIDELINES--\n\n"
                f"--BEGIN-TEXT--\n"
                f"{text}\n"
                f"--END-TEXT--\n\n"
                f"EMOJI TEXT:")

    @staticmethod
    def generate_text(guidelines: list[str]):
        """
        Generate text template
        :param guidelines: List of guidelines
        :return:
        """
        guidelines_str = ""
        for i, guideline in enumerate(guidelines):
            guidelines_str += f"{i + 1}. {guideline}\n"

        return (f"You are an agent asked with GENERATING a piece of text. You must follow the guidelines provided "
                f"below, or you will be TERMINATED. You must perform the task with an extremely high level of "
                f"ACCURACY, and MUST rely only on the provided text.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"{guidelines_str}"
                f"--END-GUIDELINES--\n\n"
                f"GENERATED TEXT:")

    @staticmethod
    def chatbot(guidelines: list[str], context: str):
        """
        Chatbot template
        :param guidelines: List of guidelines
        :return:
        """
        guidelines_str = ""
        for i, guideline in enumerate(guidelines):
            guidelines_str += f"{i + 1}. {guideline}\n"

        return (f"You are an agent asked with CHATTING with a person. You must follow the guidelines provided "
                f"below, or you will be TERMINATED. You must perform the task with an extremely high level of "
                f"ACCURACY, and MUST rely only on the provided text.\n\n"
                f"--BEGIN-GUIDELINES--\n"
                f"{guidelines_str}"
                f"--END-GUIDELINES--\n\n"
                f"--BEGIN-CONTEXT--\n"
                f"{context}\n"
                f"--END-CONTEXT--\n\n"
                f"CHATBOT RESPONSE:")
