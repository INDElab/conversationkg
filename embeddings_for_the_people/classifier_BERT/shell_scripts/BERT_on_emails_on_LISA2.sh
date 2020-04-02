#!/bin/bash


#SBATCH --job-name=BERT_on_emails

#SBATCH --time=05:00:00
#SBATCH --mem=60G

#SBATCH --nodes=1
#SBATCH --partition=gpu

##SBATCH --ntasks=1
##SBATCH --cpus-per-task=6
##SBATCH --ntasks-per-node=1



module load pre2019
module load Python/3.6.3-foss-2017b

module load CUDA/10.0.130 
module load cuDNN/7.3.1-CUDA-10.0.130


echo "Job BERT_on_emails $PBS_JOBID STARTED at `date`"



cp -r $HOME/conversationkg/embeddings_for_the_people $TMPDIR

cd $TMPDIR/embeddings_for_the_people/classifier_BERT/


for j in 0 1 2 3; do
    echo "SH: call with i=$j"
    python3 BERT_on_emails2.py --k=4 --i=$j

done



cp -r $TMPDIR/embeddings_for_the_people/classifier_BERT/ $HOME


echo "Job BERT_on_emails $PBS_JOBID ENDED at `date`"