# Handling and getting models from hugging face after training.

from huggingface_hub import login, upload_folder

# (optional) Login with your Hugging Face credentials
login()

# Push your model files
upload_folder(folder_path=".", repo_id="e1250/safety_detection", repo_type="model")
