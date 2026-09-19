# Security and Data Handling

## Training scope

This repository contains fictional laboratory procedures and controlled
documents created for software training. Do not add patient data, protected
health information, customer data, production SOPs, credentials, or proprietary
laboratory records.

## API keys

- Store the OpenAI API key only in the local `.env` file.
- Never paste a key into source code, screenshots, tickets, or chat messages.
- Never commit `.env`.
- Revoke and replace any key that may have been exposed.

## Generated artifacts

`workflow_output.json`, `retrieval_results.json`, `review_record.json`, and
`edge_case_outputs/` are excluded from source control. They may contain local
test results and reviewer information.

## Intended use

This software produces configuration drafts only. It does not validate a
laboratory method, authorize testing, approve results, or replace qualified
scientific and quality review.
