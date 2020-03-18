# Personalised GPT-2


## Motivation & Theory

- bigger idea: text as representation of entities -> entity resolution as authorship attribution
- idea for personalised GPT-2: entity is a generative process for text, a language model can capture this <br>
  -> specicially, an LM can capture $P(m|X)$ for an e-mail $m$ and a person $X$ <br>
  -> this allows for proper 
  
- idea, at least theoretically, enabled especially by large-scale pre-trained LMs such as GPT-2 <br>
  -> such LMs have extensive knowledge of the entire semantic and syntagmatic space of language and can therefore
  ground e-mails in larger linguistic context <br>
  -> such LMs have remarkably low perplexities, indicating high and detailed understanding of data they are subjected to, which leads to the expectation that they should be able to detect even subtle differences in texts such as authorship <br>
  -> potential downside: an already confident LM may be difficult to be truly adapted to the task at hand; instead such an LM
  may simply ingore additional learning signals since it already achieves low loss
 
 
 
## Implementation

### Part 0: Preparation and Splitting of Data

- author selection

- data splits

### Part 1: tuning GPT-2 on W3C e-mail corpus -> W3CGPT2

### Part 2a: tuning GPT-2 on 10 selected authors -> GPT2$_X$
 
### Part 2b: tuning W3CGPT2 on 10 selected authors -> GPT2$_X$_from_W3CGPT2

### Part 3: obtaining priors


- training details: num_epochs, 


 
## Results

### Calculations

- investigated quantities: posterior log-odds (all sorts), 