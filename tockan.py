import tiktoken

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Define the 'question' variable
question = "How many tokens are in this sentence?"

# Call the function with the defined variable
print(num_tokens_from_string(question, "cl100k_base"))
