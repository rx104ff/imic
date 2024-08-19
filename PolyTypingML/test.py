import re
# Example text
text = "Here is a string |- some 'a symbol somewhere \n and |- another 'b thing here \n but not outside."

# Dictionary mapping symbols to replacement values
replacement_dict = {
    "'a": "int",
    "'b": "float",
    # Add more mappings as needed
}

# Function to replace based on the dictionary
def replace_symbols(match):
    content = match.group(1)  # Get all content inside the closure
    for symbol, replacement in replacement_dict.items():
        if symbol in content:
            # Replace the symbol with its corresponding value
            content = content.replace(symbol, replacement)
    return f"|- {content}\n"

# Regular expression to match everything between |- and \n
pattern = re.compile(r"\|-\s*(.*?)\s*\n", re.DOTALL)

# Apply the replacement using the function
text = pattern.sub(replace_symbols, text)

print(text)