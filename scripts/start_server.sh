conda init
conda activate tracking_system


# Start redis
# docker start -ai c5b345606475297da51f2de261fd7f35ef8e7d2dbd494e9f34a9f89d385d9813

# Starting server
# pyinstrument -o "config/logs/pyinstrument_profile.html" -m uvicorn backend.main:app &
cd backend
uvicorn main:app --reload 

# Starting mlflow
# mlflow ui --backend-store-uri sqlite:///config/logs/mlflow.db & 

# Don't close
# wait