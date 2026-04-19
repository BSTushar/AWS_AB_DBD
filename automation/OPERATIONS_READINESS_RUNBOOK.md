# Operations Readiness Runbook (Intern-Level Production Hygiene)

Use this as a practical, lightweight ops playbook for demo and early production-like usage.

## 1) Daily health checks (5 minutes)

Run in management account:

```bash
BASE_URL="https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod"
curl -s "$BASE_URL/health"
curl -s "$BASE_URL/regions"
curl -s "$BASE_URL/accounts"
```

Expected:
- `/health` returns `status=ok` and non-zero `total_records` (unless intentionally empty).
- `/regions` and `/accounts` return expected scope.

## 2) CloudWatch alarms to create

Create at least these alarms:

1. **Discovery Lambda errors**
   - Metric: `AWS/Lambda`, `Errors`, Function=`db-discovery`
   - Condition: `>=1` in 1 period

2. **Discovery Lambda throttles**
   - Metric: `AWS/Lambda`, `Throttles`, Function=`db-discovery`
   - Condition: `>=1` in 1 period

3. **API Lambda errors**
   - Metric: `AWS/Lambda`, `Errors`, Function=`db-discovery-api`
   - Condition: `>=1` in 1 period

4. **Snapshot stale check** (manual/simple)
   - Verify `s3://BUCKET/discovery/inventory.json` `LastModified` within schedule interval.
   - If stale beyond 2 cycles, treat as incident.

## 3) Incident checklist

### Symptom: New account does not appear

1. Confirm Lambda env:
   - `DISCOVER_ALL_ORG_ACCOUNTS=true`
   - `ORG_SKIP_MANAGEMENT_ACCOUNT` as intended
2. Confirm account is `ACTIVE` in Organizations.
3. Confirm StackSet deployed spoke resources in that account:
   - `DBDiscoverySpokeRole`
   - `DBDiscovery` SSM document
4. Check discovery Lambda logs for AssumeRole/SSM errors.

### Symptom: Account appears but EC2 not discovered

1. EC2 must be Linux + SSM managed + online.
2. Region must be in `DISCOVERY_REGIONS`.
3. Check SSM command invocation status and stderr.

### Symptom: Dashboard stale

1. Confirm latest discovery run completed.
2. Confirm API `/health` record count changed.
3. Use dashboard Reload/Load after safety lock allows (or unlock with token).

## 4) Weekly reliability scorecard (simple)

Track these 4 numbers weekly:
- Successful discovery runs / total scheduled runs
- Failed accounts (assume-role or SSM issues)
- Time since last valid snapshot update
- API error count (`db-discovery-api` errors)

Even this lightweight scorecard is enough to show operational maturity at intern level.

