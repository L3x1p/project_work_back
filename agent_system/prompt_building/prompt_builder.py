from typing import Literal


class Prompt:
    def __init__(self):
        self.prompt_list = []  # List to store the prompt components as dictionaries

    def add_role_tag(self, role: Literal['assistant', 'user', 'system']) -> None:
        if role not in ['assistant', 'user', 'system']:
            raise ValueError(f"Invalid role '{role}'. Allowed roles are: 'assistant', 'user', 'system'.")

        # Ensure no repetitive role tags are added consecutively
        if self.prompt_list and self.prompt_list[-1]['role'] == role:
            raise ValueError(f"Duplicate role tag '{role}' cannot be added consecutively.")

        self.prompt_list.append({'role': role, 'text': ''})

    def add_instruction(self, text):
        # Ensure instructions are not added without a preceding role tag
        if not self.prompt_list or self.prompt_list[-1]['text']:
            raise ValueError("Instructions must follow a valid role tag.")

        # Add text and include the <|eot_id|> token at the end
        self.prompt_list[-1]['text'] = f"{text}\n<|eot_id|>"
        self.validate_prompt()

    def get_prompt(self):
        """
        Returns the full prompt as a string in LLaMA 3.1 format.
        """
        prompt_text = ""
        for component in self.prompt_list:
            prompt_text += f"<|start_header_id|>{component['role']}<|end_header_id|>\n"
            if component['text']:
                prompt_text += f"{component['text']}\n"
        self.validate_prompt()
        return prompt_text.strip()

    def validate_prompt(self):
        """
        Validate the prompt for the following:
        1. No repetitive role tags.
        2. Proper structure (e.g., no instructions without preceding role tags).
        """
        last_role = None

        for component in self.prompt_list:
            role = component['role']
            text = component['text']

            # Check for repetition of the same role consecutively
            if role == last_role:
                raise ValueError(f"Repetitive role tag '{role}' found consecutively.")
            last_role = role

            # Ensure instructions follow a role tag
            if not text and last_role is None:
                raise ValueError("Instructions must follow a valid role tag.")

        # print("Prompt validation successful!")

    def print_prompt(self, structure_only=False):
        """
        Prints the prompt either as full content or just its structure.

        Args:
            structure_only (bool): If True, prints only the structure (tags with ...).
                                   If False, prints the full prompt content.
        """
        if structure_only:
            print("\nPrompt Structure:")
            for component in self.prompt_list:
                print(f"<|start_header_id|>{component['role']}<|end_header_id|>")
                if component['text']:
                    print("...")
        else:
            print("\nFull Prompt:")
            print(self.get_prompt())

    def __repr__(self):
        return self.get_prompt()

    def __str__(self):
        return self.get_prompt()

    def __add__(self, other):
        """
        Adds two Prompt objects together. Ensures the result is validated.
        """
        if not isinstance(other, Prompt):
            raise TypeError("Only Prompt objects can be added.")

        # Combine the prompt lists
        combined_prompt = Prompt()
        combined_prompt.prompt_list = self.prompt_list + other.prompt_list

        # Validate the combined prompt
        combined_prompt.validate_prompt()

        return combined_prompt


if __name__ == '__main__':
    # Example Usage
    prompt1 = Prompt()

    # Adding tags and instructions
    prompt1.add_role_tag("system")
    prompt1.add_instruction("You are a helpful assistant.")
    prompt1.add_role_tag("user")
    prompt1.add_instruction("What is the capital of France?")
    prompt1.add_role_tag("assistant")
    prompt1.add_instruction("The capital of France is Paris.")

    prompt2 = Prompt()
    prompt2.add_role_tag("user")
    prompt2.add_instruction("What is 2 + 2?")
    prompt2.add_role_tag("assistant")
    prompt2.add_instruction("2 + 2 is 4.")

    # Combine prompts
    combined_prompt = prompt1 + prompt2

    # Print combined prompt with structure
    combined_prompt.print_prompt(structure_only=True)

    # Print full combined prompt
    combined_prompt.print_prompt(structure_only=False)
