# Credits & Acknowledgements

The **Warera Python Client** is made possible by the contributions, suggestions, and research of the following individuals and projects.

## Code Contributors

### 👑 Bipin Krishnan (`bipinkrish` / `Bipin`)
* **Project Creator**: Initial conception and architecture of the `warera-py-api` client library.
* **Core Systems**: Engineered the base client, asynchronous request handling, rate-limiting foundations, and testing frameworks.
* **Model Design**: Developed the core Pydantic v2 schemas, introduced nested sub-models, and implemented the `AliasChoices` parsing system for flexible API consumption.
* **CI/CD**: Configured GitHub Actions and the PyPI publishing workflows.

### 👑 PAIN (`PAIN「ᴀᴋᴀᴛsᴜᴋɪ」` / `CrucifiedPain`)
* **API Parity**: Maintained strict compliance with WarEra versions (v0.24.1 through v0.24.5-beta) and adjusted the client for new API restrictions.
* **Comprehensive Expansion**: Meticulously expanded the Pydantic schemas across the entire ecosystem, achieving 1:1 parity with the upstream TypeScript definitions (including nested classes for transactions, articles, governments, military units, and more).
* **New Features**: Implemented entirely new resource modules and schemas, including Battle Loot Summaries, Mercenary Contract Auctions, and Tournaments.
* **Documentation**: Overhauled the `README.md` and repository documentation for extreme clarity and developer ergonomics.

---

## Community & Research Acknowledgements

### 🕵️ WarEraProjects (`@wareraprojects`)
* **Feature Citing**: **Undocumented Endpoints & Wire Protocol**
* **Contribution**: The upstream [WarEraProjects/trpc](https://github.com/wareraprojects/trpc) repository was absolutely instrumental in reverse-engineering the exact structure of WarEra's undocumented API endpoints, response definitions, and the batch-request wire protocol.

### 💡 Kore-rep (`@Kore-rep`)
* **Feature Citing**: **Adaptive Rate-Limiting Engine**
* **Contribution**: Suggested the implementation of a dynamic rate-limiting engine. Because of this suggestion, the client automatically reads the `ratelimit-remaining` and `ratelimit-reset` headers from the API response and intelligently sleeps the exact amount of time required, removing the need for hardcoded delays or guessing.

---
*If you have contributed to this project and your name is missing, please open an issue or PR!*
