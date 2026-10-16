# Attribution and changes

This unofficial local adaptation is based on **IdeaScientist: Orchestrating Agents for Grounded Scientific Ideation**, Jiarui Liu and coauthors (2026).

- Paper: https://arxiv.org/abs/2610.04074v2
- Project: https://github.com/jiarui-liu/IdeaScientist
- Inspected commit: `82a98a08772eab08d11fd097445afa4a8eaaa5b3`
- Upstream license: Creative Commons Attribution-NonCommercial 4.0 International.

The role workflow has been rewritten into Chinese instructions for the host's existing tools. The report field structure from `ideascientist/vault/schema.py` and `harness/roles.py` has been converted to JSON Schema. Local citation IDs, a source ledger, and a mechanical validation helper have been added. The package is distributed under CC BY-NC 4.0 and is not endorsed by the upstream authors. It does not contain trained adapters, the Idea Vault corpus, or a running copy of the original agent harness.

Paper and dataset license declarations are distinct from the repository's license. Consult the original materials before redistributing those separate assets.
