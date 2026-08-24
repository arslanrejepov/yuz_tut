project arcthitecture is changed
```
                    ┌──────────────────────┐
                    │   Turkmen User       │
                    │ "Barmagym kesildi..."│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ NLLB Translation      │
                    │ TK → EN               │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Query Processing      │
                    │ normalization         │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌──────────────────┐
        │ Vector Search   │        │ Structured Data  │
        │ Medical RAG     │        │ Clinic/Pharmacy  │
        └────────┬────────┘        └────────┬─────────┘
                 │                          │
                 │ Relevant documents       │ Location/data
                 ▼                          │
        ┌───────────────────────────────────┐
        │        Local Open-Source LLM      │
        │        Llama / Mistral            │
        │                                   │
        │ Extract ONLY structured facts:    │
        │ - symptom                         │
        │ - body_part                       │
        │ - severity                        │
        │ - bleeding                         │
        │ - duration                         │
        │ - red_flags                       │
        └─────────────────┬─────────────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Validation Layer │
                 │ JSON Schema      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ RULE ENGINE      │
                 │                  │
                 │ severity + rules │
                 │ + location       │
                 └────────┬─────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Self-care    Pharmacy      Clinic
                                     /Emergency
             │            │            │
             └────────────┼────────────┘
                          ▼
                 ┌──────────────────┐
                 │ NLLB EN → TK     │
                 └────────┬─────────┘
                          ▼
                 ┌──────────────────┐
                 │ Turkmen UI       │
                 └──────────────────┘

```