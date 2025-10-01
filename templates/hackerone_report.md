
## Summary

{{ finding.title }}

## Description

{{ finding.description }}

## Steps To Reproduce

1. Navigate to {{ finding.affected_url }}
2. Inject the following payload into the {{ finding.affected_parameter }} parameter:
   ```
   {{ finding.payload }}
   ```
3. Observe the vulnerability manifestation

## Proof of Concept

{{ finding.proof_of_concept }}

## Impact

{{ finding.impact }}

{{ finding.business_impact }}

## Remediation

{{ finding.remediation }}

## Supporting Material/References

{% for reference in finding.references %}
- {{ reference }}
{% endfor %}

## System Information

- **Discovery Date:** {{ finding.discovery_date }}
- **CVSS Score:** {{ finding.cvss_score }}/10.0
- **CVSS Vector:** {{ finding.cvss_vector }}
- **Verification Status:** {{ finding.verification_status }}

---

*Discovered by AEGIS-X Professional Security Research*
