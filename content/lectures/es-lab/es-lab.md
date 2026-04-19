---
title: "Embedded Software Labor"
date: 2026-04-19
summary: "Durchlauf des Labors des Modules Embedded Software"
---

# Sattelite Dekodierung

This results in $x = 3y + \frac{23}{3z}$.

These are block equations:

\[a^*=x-b^*\]

\[ a^*=x-b^* \]

\[
a^*=x-b^*
\]

These are block equations using alternate delimiters:

$$a^*=x-b^*$$

$$ a^*=x-b^* $$

$$
a^*=x-b^*
$$

This is some inline code.... `msfconsole` is the command to start the Metasploit framework.


```C {linenos=inline style=vim}
int cp = 0;
int delta = 0;
int bit = 0;

for (int i = 0; i < NUM_SAT; i++) {
    delta = -1;
    bit = -1;

    for (int d = 0; d < SEQ_LEN; d++) {
        cp = 0;

        for (int j = 0; j < SEQ_LEN; j++) {
            cp += input[j + d] * chip_sequences[i][j];
        }

        if (cp > 800) {
            bit = 1;
            delta = SEQ_LEN - d;
        } else if (cp < -800) {
            bit = 0;
            delta = SEQ_LEN - d;
        } 

    }

    if (bit != -1) {
        printf("Satellite %2d has sent bit %d (delta = %d)\n", i+1, bit, delta);
    }
}
```
