def convert_to_ocean(traits_dict):
    # Calculate average scores for each trait
    traits_avg = {
        trait: sum(scores) / len(scores) if scores else 0
        for trait, scores in traits_dict.items()
    }

    # Mapping of each trait to OCEAN components and any reversals
    mappings = [
        {"trait": "Entrepreneurialism", "components": ["O", "O"], "reverse": False},
        {"trait": "Drive for Power", "components": ["C", "N"], "reverse": False},
        {"trait": "Result Orientation", "components": ["C", "C"], "reverse": False},
        {"trait": "Creativity", "components": ["O"], "reverse": False},
        {"trait": "Risk Tolerance", "components": ["E", "E"], "reverse": False},
        {"trait": "Leadership", "components": ["E", "C"], "reverse": False},
        {"trait": "Teamwork", "components": ["E", "A"], "reverse": False},
        {"trait": "Extroversion", "components": ["E"], "reverse": False},
        {"trait": "Attention to Detail", "components": ["C"], "reverse": False},
        {"trait": "Emotional Stability", "components": ["N"], "reverse": True},
        {"trait": "Ethical Guidelines", "components": ["C", "O"], "reverse": False},
    ]

    # Collect contributions for each OCEAN factor
    ocean_contributions = {"O": [], "C": [], "E": [], "A": [], "N": []}

    for mapping in mappings:
        trait = mapping["trait"]
        components = mapping["components"]
        reverse = mapping["reverse"]

        avg = traits_avg.get(trait, 0)

        for component in components:
            value = (10 - avg) if (reverse and component == "N") else avg
            ocean_contributions[component].append(value)

    # Calculate the average for each OCEAN factor
    ocean_scores = {}
    for factor in ["O", "C", "E", "A", "N"]:
        contributions = ocean_contributions[factor]
        if not contributions:
            ocean_scores[factor] = 0.0
        else:
            ocean_scores[factor] = sum(contributions) / len(contributions)

    return ocean_scores
