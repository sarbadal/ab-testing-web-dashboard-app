gcloud auth login
gcloud config set project your-project-id

gcloud functions deploy your-function-name \
  --region us-central1 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point entry_point \
  --source .
