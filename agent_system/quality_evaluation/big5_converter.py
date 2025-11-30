import json
import argparse
import sys
import numpy as np
import random
from typing import Dict, List, Any, Tuple, Optional

# Define the trait relationships as provided
TRAIT_RELATIONSHIPS = {
    "Entrepreneurialism": ["O", "O"],  # imagination (O) + action (O)
    "Drive for Power": ["C", "N"],     # striving for achievement (C) + Impulsiveness (N)
    "Result Orientation": ["C", "C"],  # sense of duty(C) + competence(C)
    "Creativity": ["O"],               # Openness to experience (O)
    "Risk Tolerance": ["E", "E"],      # Hunger for experience (E) + activity (E)
    "Leadership": ["E", "C"],          # Assertiveness (E) + self-discipline (C)
    "Teamwork": ["E", "A"],            # Sociability (E) + kindness (A)
    "Extroversion": ["E"],             # Extroversion (E)
    "Attention to Detail": ["C"],      # Conscientiousness (C)
    "Emotional Stability": ["N"],      # non-Neuroticism (N)
    "Ethical Guidelines": ["C", "O"],  # prudence (C) + values (O)
}

# Calculate trait density from relationships
TRAIT_DENSITY = {
    "C": 6,  # Appears 6 times in relationships
    "E": 5,  # Appears 5 times in relationships
    "O": 4,  # Appears 4 times in relationships
    "N": 2,  # Appears 2 times in relationships
    "A": 1   # Appears 1 time in relationships
}

def compute_big_five_scores(input_traits):
    """
    Compute Big Five scores from input traits using weighted mapping.
    
    Args:
        input_traits: Dictionary with trait scores
        
    Returns:
        Dictionary with Big Five scores on a 1-5 scale
    """
    # Adjusted trait to Big Five mapping with more balanced weights
    # Reduced weights for O and E traits, increased for N traits based on bias analysis
    trait_to_big_five = {
        "Entrepreneurialism": {"O": 1.5},  # Reduced from 1.8
        "Drive for Power": {"C": 0.4, "N": 1.6},  # Increased N from 1.4
        "Result Orientation": {"C": 0.8},
        "Creativity": {"O": 0.9},  # Reduced from 1.0
        "Risk Tolerance": {"E": 1.5},  # Reduced from 2.0
        "Leadership": {"E": 0.9, "C": 0.3},  # Reduced E from 1.2
        "Teamwork": {"E": 0.7, "A": 1.8},  # Reduced E from 0.8
        "Extroversion": {"E": 0.9},  # Reduced from 1.2
        "Attention to Detail": {"C": 0.5},
        "Emotional Stability": {"N": -0.9},  # Less negative, was -1.1
        "Ethical Guidelines": {"C": 0.4, "O": 1.0}  # Reduced O from 1.2
    }

    # Initialize scores for Big Five traits
    big_five_scores = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
    
    # Track contributions to each trait for debugging
    contributions = {"O": [], "C": [], "E": [], "A": [], "N": []}

    # Compute weighted sum for each Big Five trait
    for trait, values in input_traits.items():
        if trait in trait_to_big_five:
            # Normalize input values to 1-5 scale
            # Assuming input values are typically in range 1-10
            normalized_values = [min(5, max(1, v / 2)) for v in values]
            avg_value = sum(normalized_values) / len(normalized_values)
            
            for big_five_trait, weight in trait_to_big_five[trait].items():
                contribution = avg_value * weight
                big_five_scores[big_five_trait] += contribution
                contributions[big_five_trait].append((trait, avg_value, weight, contribution))

    # Print detailed contributions for debugging
    print("\nDetailed contributions to Big Five traits:")
    for trait, contribs in contributions.items():
        print(f"\n{trait} contributions:")
        total = 0
        for source_trait, avg_value, weight, contribution in contribs:
            print(f"  {source_trait}: {avg_value:.2f} × {weight} = {contribution:.2f}")
            total += contribution
        print(f"  Total {trait}: {total:.2f}")
    
    # Print raw scores before scaling
    print("\nRaw Big Five scores before scaling:")
    for trait, score in big_five_scores.items():
        print(f"  {trait}: {score:.2f}")

    # Adjusted expected max values based on bias analysis
    expected_max_values = {
        "O": 14,  # Increased from 12 to spread out high O scores
        "C": 10,  # Kept the same
        "E": 15,  # Increased from 12 to spread out high E scores
        "A": 9,   # Kept the same
        "N": 9    # Increased from 7 to allow for higher N scores
    }
    
    # Scale each trait to 1-5 range with a sigmoid-like curve for better differentiation
    scaled_scores = {}
    for trait, score in big_five_scores.items():
        # Apply a sigmoid-like scaling that spreads values more evenly across the range
        # This helps avoid clustering at the extremes
        max_value = expected_max_values.get(trait, 10)
        
        # Normalize to 0-1 range first
        normalized = min(1.0, max(0.0, score / max_value))
        
        # Apply sigmoid-like transformation to spread values more evenly
        # Adjusted exponents to create more balanced distributions
        if trait == "E":  # Special handling for E which tends to cluster high
            if normalized < 0.5:
                transformed = 0.5 * (normalized / 0.5) ** 0.6  # More aggressive curve for low values
            else:
                transformed = 0.5 + 0.5 * ((normalized - 0.5) / 0.5) ** 1.5  # More aggressive curve for high values
        elif trait == "O":  # Special handling for O which also clusters high
            if normalized < 0.5:
                transformed = 0.5 * (normalized / 0.5) ** 0.65
            else:
                transformed = 0.5 + 0.5 * ((normalized - 0.5) / 0.5) ** 1.4
        elif trait == "N":  # Special handling for N which tends to be low
            if normalized < 0.5:
                transformed = 0.5 * (normalized / 0.5) ** 0.8  # Less aggressive curve for low values
            else:
                transformed = 0.5 + 0.5 * ((normalized - 0.5) / 0.5) ** 1.1  # Less aggressive curve for high values
        else:  # Default handling for C and A which are already well-balanced
            if normalized < 0.5:
                transformed = 0.5 * (normalized / 0.5) ** 0.7
            else:
                transformed = 0.5 + 0.5 * ((normalized - 0.5) / 0.5) ** 1.3
            
        # Scale to 1-5 range
        scaled_value = 1 + transformed * 4
        scaled_scores[trait] = round(min(5, max(1, scaled_value)), 2)
    
    print("\nScaled Big Five scores (1-5 scale):")
    for trait, score in scaled_scores.items():
        print(f"  {trait}: {score:.2f}")
        
    return scaled_scores

def calculate_trait_weights() -> Dict[str, float]:
    """
    Calculate weights for each trait based on their relationships and density.
    
    Returns:
        Dictionary with weights for each trait
    """
    # Count occurrences of each trait in relationships
    trait_counts = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
    
    for traits in TRAIT_RELATIONSHIPS.values():
        for trait in traits:
            trait_counts[trait] += 1
    
    # Calculate weights (inverse of density - less common traits get higher weights)
    total_count = sum(trait_counts.values())
    weights = {}
    
    for trait, count in trait_counts.items():
        # Adjust weight based on density - traits that appear more often should be
        # less likely to always be at maximum
        if count > 0:
            # Higher density = lower weight to prevent always being 100
            weights[trait] = 1.0 - (count / total_count * 0.3)
        else:
            weights[trait] = 1.0
    
    return weights

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Apply density-based weights to scores.
    
    Args:
        scores: Dictionary with OCEAN trait scores
        
    Returns:
        Weighted scores
    """
    # Get trait weights
    weights = calculate_trait_weights()
    
    # Apply weights to scores
    weighted = {}
    for trait, score in scores.items():
        # Apply weight - traits with higher density get reduced more
        weighted[trait] = score * weights.get(trait, 1.0)
    
    return weighted

def fix_big5_scores(raw_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Apply density-based weights to Big 5 scores.
    
    Args:
        raw_scores: Dictionary of personality profiles with their OCEAN scores
        
    Returns:
        Weighted scores
    """
    fixed_scores = {}
    
    # Process each personality profile
    for profile, scores in raw_scores.items():
        # Apply density-based weights
        weighted = normalize_scores(scores)
        fixed_scores[profile] = weighted
    
    return fixed_scores

def calculate_derived_traits(ocean_scores: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate derived personality traits based on OCEAN scores.
    
    Args:
        ocean_scores: Dictionary with OCEAN trait scores
        
    Returns:
        Dictionary with derived trait scores on a 1-5 scale
    """
    derived_traits = {}
    
    # Handle negative N values (convert to positive emotional stability)
    emotional_stability = ocean_scores.get("N", 0)
    if emotional_stability < 0:
        emotional_stability = abs(emotional_stability)
    
    # Calculate each derived trait based on the relationships
    for trait_name, contributing_traits in TRAIT_RELATIONSHIPS.items():
        if len(contributing_traits) == 1:
            # Single trait contribution
            primary_trait = contributing_traits[0]
            if primary_trait == "N":
                # For Emotional Stability, use the adjusted value
                derived_traits[trait_name] = emotional_stability
            else:
                derived_traits[trait_name] = ocean_scores.get(primary_trait, 0)
        else:
            # Multiple trait contribution - average the values
            values = []
            for t in contributing_traits:
                if t == "N":
                    values.append(emotional_stability)
                else:
                    values.append(ocean_scores.get(t, 0))
            
            derived_traits[trait_name] = sum(values) / len(values)
    
    return derived_traits

def analyze_trait_distribution(scores_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze the distribution of traits across profiles.
    
    Args:
        scores_dict: Dictionary of personality profiles with their OCEAN scores
        
    Returns:
        Analysis results
    """
    analysis = {}
    
    # For each trait, collect all values
    for trait in "OCEAN":
        values = [scores.get(trait, 0) for scores in scores_dict.values()]
        
        analysis[trait] = {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "values": values
        }
    
    return analysis

def parse_input_scores(input_str: str) -> Dict[str, Dict[str, float]]:
    """
    Parse input string containing Big 5 scores.
    
    Args:
        input_str: String with Big 5 scores in the format shown in the example
        
    Returns:
        Dictionary of personality profiles with their OCEAN scores
    """
    scores = {}
    
    try:
        # Try parsing as JSON first
        try:
            scores = json.loads(input_str)
            return scores
        except json.JSONDecodeError:
            pass
        
        # Parse the format from the example
        lines = input_str.strip().split('\n')
        for line in lines:
            if ':' in line:
                profile, traits_str = line.split(':', 1)
                profile = profile.strip()
                
                # Parse the traits dictionary
                traits_dict = {}
                try:
                    # Try to evaluate the Python dictionary
                    traits_dict = eval(traits_str.strip())
                except:
                    # If that fails, try to parse it manually
                    traits_str = traits_str.strip().strip('{}')
                    trait_pairs = traits_str.split(',')
                    for pair in trait_pairs:
                        if ':' in pair:
                            trait, value = pair.split(':', 1)
                            trait = trait.strip().strip("'\"")
                            value = float(value.strip())
                            traits_dict[trait] = value
                
                scores[profile] = traits_dict
        
        return scores
    except Exception as e:
        print(f"Error parsing input: {str(e)}")
        return {}

def parse_input_traits(input_str: str) -> Dict[str, Dict[str, List[int]]]:
    """
    Parse input string containing trait scores.
    
    Args:
        input_str: String with trait scores
        
    Returns:
        Dictionary of personality profiles with their trait scores
    """
    traits = {}
    
    try:
        # Try parsing as JSON first
        try:
            traits = json.loads(input_str)
            return traits
        except json.JSONDecodeError:
            pass
        
        # Try to parse Python dictionary format
        try:
            traits = eval(input_str)
            return traits
        except:
            pass
        
        # Parse line by line
        lines = input_str.strip().split('\n')
        current_profile = None
        current_traits = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(':'):
                # New profile
                if current_profile and current_traits:
                    traits[current_profile] = current_traits
                current_profile = line[:-1].strip()
                current_traits = {}
            elif ':' in line and current_profile:
                # Trait line
                trait, values_str = line.split(':', 1)
                trait = trait.strip()
                
                # Parse values
                try:
                    values = eval(values_str.strip())
                    if isinstance(values, list):
                        current_traits[trait] = values
                except:
                    # Try to parse manually
                    values_str = values_str.strip().strip('[]')
                    values = [int(v.strip()) for v in values_str.split(',') if v.strip().isdigit()]
                    if values:
                        current_traits[trait] = values
        
        # Add the last profile
        if current_profile and current_traits:
            traits[current_profile] = current_traits
        
        return traits
    except Exception as e:
        print(f"Error parsing input traits: {str(e)}")
        return {}

def save_results_to_file(
    filename: str, 
    fixed_scores: Dict[str, Dict[str, float]], 
    derived_traits: Dict[str, Dict[str, float]],
    raw_scores: Dict[str, Dict[str, float]] = None,
    input_traits: Dict[str, Dict[str, List[int]]] = None
) -> None:
    """
    Save results to a JSON file.
    
    Args:
        filename: Output filename
        fixed_scores: Fixed OCEAN scores
        derived_traits: Derived personality traits
        raw_scores: Raw OCEAN scores (optional)
        input_traits: Input trait scores (optional)
    """
    results = {
        "ocean_scores": fixed_scores,
        "derived_traits": derived_traits
    }
    
    if raw_scores:
        results["raw_ocean_scores"] = raw_scores
        
    if input_traits:
        results["input_traits"] = input_traits
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")

def process_trait_scores(trait_scores: Dict[str, Dict[str, List[int]]]) -> Dict[str, Dict[str, float]]:
    """
    Process trait scores to compute Big Five scores.
    
    Args:
        trait_scores: Dictionary of personality profiles with their trait scores
        
    Returns:
        Dictionary of personality profiles with their Big Five scores
    """
    big_five_scores = {}
    
    for profile, traits in trait_scores.items():
        big_five_scores[profile] = compute_big_five_scores(traits)
    
    return big_five_scores

def generate_random_profiles(num_profiles: int = 100) -> Dict[str, Dict[str, List[int]]]:
    """
    Generate random personality profiles for testing bias in the conversion algorithm.
    
    Args:
        num_profiles: Number of random profiles to generate
        
    Returns:
        Dictionary of profiles with random trait scores
    """
    traits = [
        "Teamwork", "Creativity", "Leadership", "Extroversion", "Risk Tolerance",
        "Drive for Power", "Entrepreneurialism", "Ethical Guidelines", 
        "Result Orientation", "Attention to Detail", "Emotional Stability"
    ]
    
    profiles = {}
    
    for i in range(num_profiles):
        profile_id = f"Profile_{i+1}"
        profile = {}
        
        for trait in traits:
            # Determine number of values (1-3) for this trait
            num_values = random.randint(1, 3)
            
            # Generate random values between 1-10 with different distributions
            # to ensure we have a wide variety of profiles
            if random.random() < 0.2:  # 20% chance of low values
                values = [random.randint(1, 4) for _ in range(num_values)]
            elif random.random() < 0.4:  # 20% chance of high values
                values = [random.randint(7, 10) for _ in range(num_values)]
            else:  # 60% chance of mid-range values with variation
                values = [random.randint(3, 8) for _ in range(num_values)]
            
            profile[trait] = values
        
        profiles[profile_id] = profile
    
    return profiles

def analyze_bias(scores_dict: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
    """
    Analyze potential bias in the Big Five scores across many profiles.
    
    Args:
        scores_dict: Dictionary of personality profiles with their OCEAN scores
        
    Returns:
        Dictionary with bias analysis results
    """
    # Initialize counters for highest trait in each profile
    highest_trait_counts = {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0}
    
    # Initialize lists to store all values for each trait
    all_values = {"O": [], "C": [], "E": [], "A": [], "N": []}
    
    # Analyze each profile
    for profile, scores in scores_dict.items():
        # Find the highest trait
        highest_trait = max(scores.items(), key=lambda x: x[1])[0]
        highest_trait_counts[highest_trait] += 1
        
        # Store all values
        for trait, value in scores.items():
            all_values[trait].append(value)
    
    # Calculate statistics
    stats = {}
    for trait, values in all_values.items():
        stats[trait] = {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "median": sorted(values)[len(values) // 2],
            "std_dev": np.std(values),
            "highest_count": highest_trait_counts[trait],
            "highest_percentage": (highest_trait_counts[trait] / len(scores_dict)) * 100
        }
    
    return stats

def convert_traits_to_ocean(traits_data: Dict[str, Dict[str, List[int]]]) -> Dict[str, Dict[str, Any]]:
    """
    Convert trait data to OCEAN scores and return both the original traits and converted scores.
    
    Args:
        traits_data: Dictionary of profiles with their trait scores
        
    Returns:
        Dictionary containing original traits, raw OCEAN scores, and weighted OCEAN scores
    """
    # Process trait scores to get raw OCEAN scores
    raw_scores = process_trait_scores(traits_data)
    
    # Apply density-based weights
    weighted_scores = fix_big5_scores(raw_scores)
    
    # Calculate derived traits
    derived_traits = {}
    for profile, scores in weighted_scores.items():
        derived_traits[profile] = calculate_derived_traits(scores)
    
    # Prepare the result
    result = {
        "original_traits": traits_data,
        "raw_ocean_scores": raw_scores,
        "weighted_ocean_scores": weighted_scores,
        "derived_traits": derived_traits
    }
    
    return result

def convert_ocean_to_derived(ocean_scores: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, Any]]:
    """
    Convert OCEAN scores to derived traits and return both.
    
    Args:
        ocean_scores: Dictionary of profiles with their OCEAN scores
        
    Returns:
        Dictionary containing original OCEAN scores, weighted OCEAN scores, and derived traits
    """
    # Apply density-based weights
    weighted_scores = fix_big5_scores(ocean_scores)
    
    # Calculate derived traits
    derived_traits = {}
    for profile, scores in weighted_scores.items():
        derived_traits[profile] = calculate_derived_traits(scores)
    
    # Prepare the result
    result = {
        "original_ocean_scores": ocean_scores,
        "weighted_ocean_scores": weighted_scores,
        "derived_traits": derived_traits
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Convert personality traits to Big 5 scores")
    parser.add_argument("--input", help="Input file with personality scores")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--traits", action="store_true", help="Input contains trait scores instead of Big 5 scores")
    parser.add_argument("--verbose", action="store_true", help="Show detailed analysis")
    parser.add_argument("--generate", type=int, help="Generate random profiles for bias testing")
    parser.add_argument("--api", action="store_true", help="Run in API mode (returns JSON)")
    args = parser.parse_args()
    
    # Generate random profiles if requested
    if args.generate:
        print(f"Generating {args.generate} random profiles for bias testing...")
        random_profiles = generate_random_profiles(args.generate)
        
        # Process the random profiles
        raw_scores = process_trait_scores(random_profiles)
        fixed_scores = fix_big5_scores(raw_scores)
        
        # Analyze for bias
        print("\nBias Analysis:")
        bias_stats = analyze_bias(fixed_scores)
        
        # Print bias analysis results
        print("\nDistribution of highest traits across profiles:")
        for trait, stats in bias_stats.items():
            print(f"{trait}: {stats['highest_count']} profiles ({stats['highest_percentage']:.1f}%)")
        
        print("\nStatistics for each trait:")
        for trait, stats in bias_stats.items():
            print(f"\n{trait}:")
            print(f"  Range: {stats['min']:.2f} - {stats['max']:.2f}")
            print(f"  Average: {stats['avg']:.2f}")
            print(f"  Median: {stats['median']:.2f}")
            print(f"  Standard Deviation: {stats['std_dev']:.2f}")
        
        # Save random profiles to file if output is specified
        if args.output:
            all_derived_traits = {}
            for profile, scores in fixed_scores.items():
                all_derived_traits[profile] = calculate_derived_traits(scores)
            
            save_results_to_file(args.output, fixed_scores, all_derived_traits, raw_scores, random_profiles)
            print(f"\nResults saved to {args.output}")
        
        return
    
    # Process the 4 original profiles
    if args.input:
        input_file = args.input
        with open(input_file, 'r') as f:
            input_str = f.read()
    else:
        # Use sample data if no input file is provided
        if args.traits:
            # Sample trait scores for the 4 original profiles
            input_str = """
Cl: {
  "Teamwork": [5, 5], 
  "Creativity": [2, 2, 2], 
  "Leadership": [3, 2, 2],
  "Extroversion": [4, 3, 3], 
  "Risk Tolerance": [2, 2], 
  "Drive for Power": [3, 3, 2],
  "Entrepreneurialism": [2, 3], 
  "Ethical Guidelines": [5, 5, 4], 
  "Result Orientation": [6, 5, 4],
  "Attention to Detail": [6, 5, 5], 
  "Emotional Stability": [5, 5, 5]
}

Se: {
  "Teamwork": [1, 1], 
  "Creativity": [6, 6, 5], 
  "Leadership": [8, 7, 7],
  "Extroversion": [3, 3, 3], 
  "Risk Tolerance": [9, 8], 
  "Drive for Power": [10, 10, 9],
  "Entrepreneurialism": [8, 9], 
  "Ethical Guidelines": [2, 2, 1], 
  "Result Orientation": [9, 9, 8],
  "Attention to Detail": [6, 6, 6], 
  "Emotional Stability": [7, 7, 6]
}

Sa: {
  "Teamwork": [3, 2], 
  "Creativity": [9, 9, 10], 
  "Leadership": [4, 3, 2],
  "Extroversion": [1, 1, 2], 
  "Risk Tolerance": [2, 3], 
  "Drive for Power": [3, 2, 1],
  "Entrepreneurialism": [4, 5], 
  "Ethical Guidelines": [9, 8, 9], 
  "Result Orientation": [8, 7, 8],
  "Attention to Detail": [9, 9, 9], 
  "Emotional Stability": [7, 6, 7]
}

Ge: {
  "Teamwork": [4, 4], 
  "Creativity": [10, 10, 10], 
  "Leadership": [5, 5, 4],
  "Extroversion": [6, 5, 5], 
  "Risk Tolerance": [5, 4], 
  "Drive for Power": [5, 6, 6],
  "Entrepreneurialism": [7, 7], 
  "Ethical Guidelines": [6, 5, 5], 
  "Result Orientation": [10, 9, 10],
  "Attention to Detail": [10, 10, 10], 
  "Emotional Stability": [7, 6, 7]
}
            """
        else:
            # Sample Big 5 scores for the 4 original profiles
            input_str = """
Cl: {'O': 3.5, 'C': 4.2, 'E': 3.8, 'A': 2.9, 'N': 1.8}
Se: {'O': 3.6, 'C': 4.1, 'E': 4.8, 'A': 1.5, 'N': 2.7}
Sa: {'O': 4.8, 'C': 3.9, 'E': 2.5, 'A': 1.9, 'N': 1.2}
Ge: {'O': 4.2, 'C': 4.5, 'E': 3.7, 'A': 2.1, 'N': 2.3}
            """
    
    # Process input based on type
    if args.traits:
        print("Processing trait scores...")
        input_traits = parse_input_traits(input_str)
        result = convert_traits_to_ocean(input_traits)
        raw_scores = result["raw_ocean_scores"]
        fixed_scores = result["weighted_ocean_scores"]
        all_derived_traits = result["derived_traits"]
    else:
        print("Processing Big 5 scores...")
        raw_scores = parse_input_scores(input_str)
        result = convert_ocean_to_derived(raw_scores)
        fixed_scores = result["weighted_ocean_scores"]
        all_derived_traits = result["derived_traits"]
        input_traits = None
    
    # If in API mode, just return the JSON result
    if args.api:
        print(json.dumps(result, indent=2))
        return
    
    # Print results
    print("\nOCEAN Scores (1-5 scale):")
    print(json.dumps(fixed_scores, indent=2))
    
    print("\nDerived Personality Traits (1-5 scale):")
    print(json.dumps(all_derived_traits, indent=2))
    
    # Show detailed analysis if requested
    if args.verbose:
        print("\nTrait Analysis:")
        analysis = analyze_trait_distribution(fixed_scores)
        for trait, stats in analysis.items():
            print(f"{trait}: min={stats['min']:.2f}, max={stats['max']:.2f}, avg={stats['avg']:.2f}")
    
    # Save results if output file is specified
    if args.output:
        save_results_to_file(args.output, fixed_scores, all_derived_traits, raw_scores, input_traits)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main() 