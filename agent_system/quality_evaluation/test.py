from agent_system.quality_evaluation.job_orientation_results import get_best_fit_second_level_categories

import json
result = get_best_fit_second_level_categories(1, None)
print(json.dumps(result, indent=4))
