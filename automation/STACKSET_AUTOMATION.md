# Spoke Automation with CloudFormation StackSets

Use this to bootstrap spoke accounts in bulk (role + SSM document + EC2 SSM role/profile), so onboarding new accounts is mostly one command.

## What this creates in each spoke account/region

- `DBDiscoverySpokeRole` (assumable by management account)
- `EC2-SSM-Discovery-Role`
- `EC2-SSM-Discovery-InstanceProfile`
- `DBDiscovery` SSM document

Template path:

- `automation/spoke-bootstrap-stackset.yaml`

## Prerequisites

1. You are in the **management account**.
2. AWS Organizations is enabled and member accounts are created.
3. CloudFormation trusted access for Organizations is enabled (service-managed StackSets).
4. Discovery script exists at `s3://<BUCKET>/ssm/discovery_python.py`.

## Multi-region note

**IAM is global per account.** Deploying the same IAM roles from two regional stacks used to fail on “already exists.”  
The template now takes **`PrimaryRegionForIam`** (default `ap-south-1`): IAM + instance profile are created **only** in that region; **`DBDiscovery`** SSM document is still created **in every** StackSet region so Run Command works where your EC2 runs.

Match **`PrimaryRegionForIam`** to one of your StackSet regions (usually the first / main region).  
**Always include that region** in the StackSet target region list, or IAM will never be created.

## Create StackSet (management account)

```bash
aws cloudformation create-stack-set \
  --stack-set-name task02-spoke-bootstrap \
  --template-body file://automation/spoke-bootstrap-stackset.yaml \
  --permission-model SERVICE_MANAGED \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters \
    ParameterKey=ManagementAccountId,ParameterValue=123456789012 \
    ParameterKey=BucketName,ParameterValue=my-db-discovery-bucket \
    ParameterKey=PrimaryRegionForIam,ParameterValue=ap-south-1
```

## Deploy to specific account IDs and regions

```bash
aws cloudformation create-stack-instances \
  --stack-set-name task02-spoke-bootstrap \
  --deployment-targets Accounts=111111111111,222222222222,333333333333 \
  --regions ap-south-1 eu-west-1 \
  --operation-preferences FailureToleranceCount=0,MaxConcurrentCount=1
```

## Deploy to an OU (recommended after initial test)

```bash
aws cloudformation create-stack-instances \
  --stack-set-name task02-spoke-bootstrap \
  --deployment-targets OrganizationalUnitIds=ou-xxxx-yyyyyyyy \
  --regions ap-south-1 eu-west-1
```

## Verify

In each spoke account:

1. IAM role `DBDiscoverySpokeRole` exists with trust to management account.
2. IAM role `EC2-SSM-Discovery-Role` exists and includes `AmazonSSMManagedInstanceCore`.
3. SSM document `DBDiscovery` exists.

Then in management account:

1. Set `db-discovery` Lambda env vars for org auto-onboarding:
   - `DISCOVER_ALL_ORG_ACCOUNTS=true`
   - `ORG_SKIP_MANAGEMENT_ACCOUNT=true` (recommended)
   - optional `ORG_EXCLUDE_ACCOUNT_IDS=...`
2. Keep `SPOKE_ACCOUNTS` empty (or only special non-org accounts).
3. Run test event `{}`.
4. Confirm S3 `discovery/inventory.json` includes newly bootstrapped spoke account IDs.

## Recreate StackSet cleanly (CLI)

When the console won’t update the template, use PowerShell from the repo root after **no StackSet operation is RUNNING**:

```powershell
.\automation\recreate-stackset.ps1
```

Optional: `-BucketName "your-bucket"`. Edit active/suspended account IDs at the top of the script if yours differ.

## Notes

- Account creation itself (email ownership/verification) still has manual/governance steps.
- If resources already exist with the same names, StackSet creation for those accounts may fail; remove/rename conflicts and retry.
- For true zero-touch onboarding of new member accounts, target an OU with StackSet auto-deployment and keep discovery in org mode (`DISCOVER_ALL_ORG_ACCOUNTS=true`).
