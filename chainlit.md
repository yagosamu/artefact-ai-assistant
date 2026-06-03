# AI Assistant with Tool Use

A small AI assistant that decides when to answer from its own knowledge and when to call external tools.

**Available tools**
- `calculator` — arithmetic, percentages, any numerical computation
- `currency_converter` — convert between currencies using live ECB rates

**Try these**
- *Who was Marie Curie?* — direct LLM answer
- *What is 128 times 46?* — uses the calculator
- *How much is 100 EUR in BRL?* — uses the currency converter
- *Convert 1000 USD to BRL and add a 5% fee* — chains both tools

The agent matches the language of your question (try in Portuguese!).

Built as a take-home challenge for Artefact. [Source on GitHub](https://github.com/yagosamu/artefact-ai-assistant)