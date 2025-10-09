from google.cloud import asset_v1
from datetime import datetime, timezone, timedelta

def sa_key_check(request):
    GCP_ORGANIZATION_ID = "206587515385"
    scope = f"organizations/{GCP_ORGANIZATION_ID}"

    # Look for keys expiring in the next 30 days.
    EXPIRATION_WINDOW_DAYS = 1000
    expiration_window_seconds = timedelta(days=EXPIRATION_WINDOW_DAYS).total_seconds()

    client = asset_v1.AssetServiceClient()
    service_account_key_asset_type = "iam.googleapis.com/ServiceAccountKey"

    key_response = client.search_all_resources(
        request={
            "scope": scope,
            "asset_types": [service_account_key_asset_type],
            "read_mask": "*",
        }
    )

    expiring_keys = []
    now = datetime.now(timezone.utc)

    for key in key_response:
        if not key.versioned_resources:
            continue

        key_version = key.versioned_resources[0]

        valid_before_time = key_version.resource.get('validBeforeTime')
        # Non-expiring keys have a far-future expiry date or no expiry.
        if not valid_before_time or valid_before_time == "9999-12-31T23:59:59Z":
            continue

        expiry_date = datetime.fromisoformat(valid_before_time.replace('Z', '+00:00'))
        seconds_until_expiry = (expiry_date - now).total_seconds()

        # Only include keys that expire within our window and have not already expired.
        if 0 < seconds_until_expiry <= expiration_window_seconds:
            key_info = f"Service Account: {key.parent_full_resource_name.split('/')[-1]}, Key: {key.name}, Expires in (seconds): {int(seconds_until_expiry)}"
            expiring_keys.append(key_info)

    result_string = f"Found {len(expiring_keys)} expiring keys: " + "; ".join(expiring_keys)
    print(result_string)
    return "Function executed successfully."