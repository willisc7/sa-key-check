from google.cloud import asset_v1
import datetime

def sa_key_check(request):
    GCP_ORGANIZATION_ID = "206587515385"
    scope = f"organizations/{GCP_ORGANIZATION_ID}"

    # SECONDS_IN_A_YEAR = 365 * 24 * 60 * 60
    SECONDS_IN_A_YEAR = 30 * 24 * 60 * 60

    client = asset_v1.AssetServiceClient()
    service_account_key_asset_type = "iam.googleapis.com/ServiceAccountKey"

    key_response = client.search_all_resources(
        request={
            "scope": scope,
            "asset_types": [service_account_key_asset_type],
            "read_mask": "*",
        }
    )

    for key in key_response:
        key_version = key.versioned_resources.pop()

        validBeforeTime = key_version.resource.get('validBeforeTime', 'N/A')
        if validBeforeTime == 'N/A':
            # This is a non-expiring key, so we can skip it.
            continue

        seconds_until_expiry = int((datetime.datetime.fromisoformat(validBeforeTime.replace('Z', '+00:00'))- datetime.datetime.now(datetime.timezone.utc)).total_seconds())

        # Only print keys that expire in the next year and have not already expired.
        if 0 < seconds_until_expiry <= SECONDS_IN_A_YEAR:
            print(f"{key.parent_full_resource_name.split('/')[-1]},{key.name},{seconds_until_expiry}")