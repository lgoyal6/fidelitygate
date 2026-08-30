# Synthetic operational policies

These policies are synthetic benchmark evidence. They are intentionally concise so every executable claim can cite an exact approved sentence. They are not legal, medical, financial, or operational advice.

<a id="refund-high_value_approval"></a>
## Refund approval

A refund above $1,000 must not be issued until a manager approves it.

<a id="purchase-separation_of_duties"></a>
## Purchase separation of duties

The requester and approver for a purchase must be different people.

<a id="export-consent_required"></a>
## Export consent

Do not export personal data unless the subject's consent is recorded.

<a id="access-expiry_enforced"></a>
## Access expiry

Once a grant expires, every role must be denied until a new grant is issued.

<a id="invoice-single_payout"></a>
## Invoice idempotency

Retries must be idempotent: never pay the same invoice more than once.

<a id="expense-receipt_threshold"></a>
## Expense evidence threshold

A receipt is mandatory before approving any expense over $500.

<a id="incident-remediation_before_close"></a>
## Incident closure

A SEV-1 incident remains open until the remediation record is attached.

<a id="deployment-health_before_promotion"></a>
## Deployment health

Promotion is allowed only after the candidate has a passing health check.

<a id="recovery-same_tenant"></a>
## Account-recovery tenant isolation

A password reset is valid only when identity was verified in the target tenant.

<a id="vendor-dpa_before_disclosure"></a>
## Vendor disclosure

Record an approved data processing agreement before any PII disclosure.

<a id="medication-pharmacist_verification"></a>
## Medication release

A high-risk medication order must be verified by a pharmacist before release.

<a id="memory-episode_isolation"></a>
## Episode memory isolation

Starting a new episode clears sensitive memory from every earlier episode.

<a id="reward-only_after_completion"></a>
## Reward grounding

Award positive reward only after the task is verified and completed.

<a id="operation-audit_required"></a>
## Privileged-operation observability

A privileged operation and its audit record must be committed together.

<a id="stress-approval_before_issue"></a>
## Search stress approval

A submitted sensitive request must receive manager approval before issuance.
