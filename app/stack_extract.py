def extract_stacks(title, description, skills_csv):
    text = " ".join(filter(None, [title, description, skills_csv])).lower()
    stacks = []
    for k in ["react","next","typescript","node","php","wordpress"]:
        if k in text:
            stacks.append(k)
    return stacks
