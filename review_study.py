import optuna

storage_name = "sqlite:///data/optuna_study.db"

try:
    # Get a list of all studies
    all_studies = optuna.get_all_study_summaries(storage=storage_name)
    for study in all_studies:
        print(study.study_name)

    if not all_studies:
        print("No studies found in the database.")
    else:
        # Correctly get the last study from the list
        latest_study_summary = all_studies[-1]
        study_name = latest_study_summary.study_name
        
        print(f"--- Loading most recent study: {study_name} ---")

        # Load the specific study
        study = optuna.load_study(study_name=study_name, storage=storage_name)
        
        print(f"\nBest trial from this study: {study_name}")
        print(f"  Value (loss): {study.best_value}")
        print("  Params: ")
        for key, value in study.best_params.items():
            print(f"    {key}: {value}")

except Exception as e:
    print(f"An error occurred: {e}")
