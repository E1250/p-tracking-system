# Handling and getting models from hugging face after training.

from huggingface_hub import hf_hub_download


def hf_fetch_model(repo_id: str, filename: str) -> str:
    """
    repo_id:
        str: hf repository id
    filename:
        str: file name in the repo
    return
        str: download path
    """
    return hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=".cache")


def hf_upload_model():
    pass
