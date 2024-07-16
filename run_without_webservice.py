from pprint import pprint

# Run
inputs = {"question": "What are the types of agent memory?"}
for output in app.stream(inputs):
    for key, value in output.items():
        # Node
        pprint(f"Node '{key}':")
        # Optional: print full state at each node
        # pprint.pprint(value["keys"], indent=2, width=80, depth=None)
    pprint("\n---\n")

# Final generation
pprint(value["generation"])
ss
# Expected output:
""" 
  ---ROUTE QUESTION---
  ---ROUTE QUESTION TO RAG---
  ---RETRIEVE---
  "Node 'retrieve':"
  '\n---\n'
  ---CHECK DOCUMENT RELEVANCE TO QUESTION---
  ---GRADE: DOCUMENT RELEVANT---
  ---GRADE: DOCUMENT RELEVANT---
  ---GRADE: DOCUMENT NOT RELEVANT---
  ---GRADE: DOCUMENT RELEVANT---
  ---ASSESS GRADED DOCUMENTS---
  ---DECISION: GENERATE---
  "Node 'grade_documents':"
  '\n---\n'
  ---GENERATE---
  ---CHECK HALLUCINATIONS---
  ---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---
  ---GRADE GENERATION vs QUESTION---
  ---DECISION: GENERATION ADDRESSES QUESTION---
  "Node 'generate':"
  '\n---\n'
  ('The types of agent memory include Sensory Memory, Short-Term Memory (STM) or '
  'Working Memory, and Long-Term Memory (LTM) with subtypes of Explicit / '
  'declarative memory and Implicit / procedural memory. Sensory memory retains '
  'sensory information briefly, STM stores information for cognitive tasks, and '
  'LTM stores information for a long time with different types of memories.')
"""