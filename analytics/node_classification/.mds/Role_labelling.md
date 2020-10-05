# Role Labelling

The node classification task is a proxy for the identification of roles of the people in our email corpus. We perform role labelling according to simple heuristics on the EmailKG. Recovering these labels on the TextKG is the node classification task. In this section, we describe the details of these heuristics.


## ConfirmedPerson

One of the most basic questions to ask is whether we can infer from TextKG, which of the person entities in it also appeared as either senders or receivers in the EmailKG. That is, which of the person entities the NER algorithm found in the emails' bodies is a confirmed person. 

Every person entity in the EmailKG receives the label 0, any other person entity in the 
