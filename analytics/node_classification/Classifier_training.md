# Setup



## Network Parameters

- embedding size

- number of layers



## Training Parameters

### number of epochs
  the number of iterations over the training data set before convergence/overfitting is reached
  500 typically leads to significant convergence
  
  
### loss
  cross entropy (reduces to `-log P(c|x)` w. `c` the true class of example `x`)
  no tuneable parameters, except weights, see below
  
### weights applied to the cross-entropy loss
  a distribution over the output classes which dictates the contribution of each class to the overall loss:



### regularisation: L2 norm (equiv. to Euclidean distance from the origin) on the node embeddings, coefficient: 2.0

### Try



