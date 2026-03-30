conda init
conda activate tracking_system

# Starting server
# pyinstrument -o "config/logs/pyinstrument_profile.html" -m uvicorn backend.main:app &
uvicorn backend.main:app --reload 

# Starting mlflow
# mlflow ui --backend-store-uri sqlite:///config/logs/mlflow.db & 

# Don't close
# wait