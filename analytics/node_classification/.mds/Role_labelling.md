# Role Labelling

The node classification task is a proxy for the identification of roles of the people in our email corpus. We perform role labelling according to simple heuristics on the EmailKG. Recovering these labels on the TextKG is the node classification task. In this section, we describe the details of these heuristics.

## Labelling Functions

A labelling function 


## Some Nodes in the Graph have no Role Labels

There are two cases in which a node in the TextKG does not receive a label:

  1. The node is of type Person but it does not occur in EmailKG and has therefore not been assigned a role label.
  2. The node is not of type Person and role labelling is therefore not applicable.
  
We make the labelling function obtained from the EmailKG total by defining additional labels for these two cases and assigning them to any nodes to which they apply. So for any of the heuristics


## ConfirmedPerson

One of the most basic questions to ask is whether we can infer from the TextKG, which of the person entities in it also appeared as either senders or receivers in the EmailKG. That is, which of the person entities the NER algorithm found in the emails' bodies is a confirmed person. 

This heuristic knows only one label: for any person entity evidenced by the EmailKG.


## MajorOrganisation

One of the more interesting latent roles are the organisations to which people belong. In this heuristic, we assign the same to persons who belong to the same organisation according to the EmailKG (where the name of the organisation of a person is the domain name in their email address, e.g. john@w3.org belongs to the organisation 'w3').

For this heuristic, we first identify the $n$ most frequent organisations in EmailKG and assign labels to the people who belong to any of these. All the remaining people in the EmailKG receive the $n+1$th label with the interpretation 'does not belong to a major organisation'.

It is worth noting that most people in the EmailKG (for any email corpus) do not belong to a major organisation. In fact, the frequency distribution over organisations follows roughly a power law distribution.


## RolesFromGraphMeasure





