Service Account needs `Cloud Asset Viewer` permissions at the org level

```
gcloud services enable artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com \
  cloudasset.googleapis.com
```

```
gcloud run deploy sa-key-check \
      --source . \
      --region us-central1 \
      --allow-unauthenticated \
      --function sa_key_check
```