## Memorization (Over-fitting & Direct Recall)

- Memorization occurs when a model stores specific data points, verbatim sequences, or exact inputs directly within its parameters (weights) rather than learning underlying structures.

    - Mechanism: High-capacity neural networks can act as high-dimensional lookup tables. If a model is over-parameterized or trained for too many epochs without regularization, it minimizes loss by "hardcoding" exact relationships.

    - Manifestation in LLMs: Verbatim reproduction of copyrighted passages, phone numbers, or training data prompts.

    - Manifestation in ML: Perfect performance on training data (100% accuracy) with severe drop-offs on validation/test data (overfitting).

    - When it is useful: Storing factual ground truth, precise syntax, historical dates, or unique identifiers where approximation leads to hallucinations or errors.

    - When it is detrimental: Reduces generalization, increases privacy leakage risks (membership inference attacks), and makes models fragile to tiny variations in input data (adversarial perturbations).

## Association
![alt text](image-1.png)
![alt text](image-3.png)

## Verbatim sequences
![alt text](image-2.png)

## Online learning
![alt text](image-4.png)

## Attack procedures without jailbreaking
- Categories of attacks
- ![alt text](image-5.png)
- Attack methods under that category
- ![alt text](image-6.png)

## flow
  1. Dictionary with PUBLIC data (what the attacker already knows)
  2. Pick 3 examples from it at RANDOM (no scoring)
  3. Build prompt = question + the 3 example records + the target's record line
  4. Send the prompt to the DUMMY SERVER ONLY (never attacks Groq)
  5. Analyze the reply: does it contain the required PII?
  6. Replace one of the 3 picked examples with the new (question -> PII) pair
  7. Repeat with the next name (3 names total)