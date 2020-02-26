#!/bin/bash


#SBATCH --job-name=BERT_on_emails

#SBATCH --time=10:00:00
#SBATCH --mem=40G

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --ntasks-per-node=1

##SBATCH --partition=gpu_shared
##SBATCH --gres=gpu:1



module load pre2019
module load Python/3.6.3-foss-2017b

#module load CUDA/10.0.130 
#module load cuDNN/7.3.1-CUDA-10.0.130


echo "Job BERT_on_emails $PBS_JOBID started at `date`"


cp -r $HOME/work/conversationkg/embeddings_for_the_people $TMPDIR

cd $TMPDIR/embeddings_for_the_people/raw_BERT


for j in 0 1 2 3; do
    python3 BERT_on_emails_on_LISA.py --k=4 --i=$j &
    echo "started process with i=$j"
done

wait

cp -r $TMPDIR/embeddings_for_the_people/raw_BERT $HOME


