# Architecture

```text
START
  |
  v
ORCHESTRATOR
  | competitors = [A, B, C]
  |
  +---- Send(A) ---> LEAD RESEARCHER A ---+
  +---- Send(B) ---> LEAD RESEARCHER B ---+--> operator.add --> ANALYST
  +---- Send(C) ---> LEAD RESEARCHER C ---+
                                             |
                                             v
                                      HUMAN REVIEW
                                             |
                                      approve/edit
                                             |
                                             v
                                        COPYWRITER
                                             |
                                             v
                                            END
```

`InMemorySaver` stores checkpointed graph state for a thread. `InMemoryStore` stores application data across threads during the process lifetime.
