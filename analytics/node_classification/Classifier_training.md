# Setup



## Network Parameters

### embedding size
  number of dimensions of the entity embedding space <br>
  low dimensionality fits the low number of classes (usually between 5 and 10) and is convenient for subsequent visualisation in 3D space: 4 dimensions
  
  
### number of layers
  then RGCN in Thiviyan's implementation can have either one or two convolutional layers (on top of the embedding layer) <br>
  more layers = more learning power: 2 layers


## Training Parameters

### number of epochs
  the number of iterations over the training data set before convergence/overfitting is reached <br>
  500 typically leads to significant convergence
  
  
### loss
  cross entropy (reduces to `-log P(c|x)` w. `c` the true class of example `x`) <br>
  no tuneable parameters, except weights, see below
  
### weights applied to the cross-entropy loss
  a distribution over the output classes which dictates the contribution of each class to the overall loss <br>
  each relevant class is given a value of 10, each irrelevant one (non-person entity, unlabeled person) a value of 1, 
  the resulting vector is re-normalised to be a distribution
  

### regularisation
  L2 norm (equiv. to Euclidean distance from the origin) on the node embeddings, added to the raw loss <br>
  coefficient in the addition 2.0

## Try
