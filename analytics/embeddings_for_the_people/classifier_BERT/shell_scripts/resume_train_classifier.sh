#!/bin/bash


#SBATCH --job-name=train_classifier_BERT

#SBATCH --time=42:00:00
#SBATCH --mem=60G

#SBATCH --nodes=1
# #SBATCH --partition=gpu
#SBATCH --partition=gpu_shared
#SBATCH --gres=gpu:1


##SBATCH --ntasks=1
##SBATCH --cpus-per-task=6
##SBATCH --ntasks-per-node=1



module load pre2019
module load Python/3.6.3-foss-2017b

module load CUDA/10.0.130 
module load cuDNN/7.3.1-CUDA-10.0.130


echo "Job resuming train_classifier_BERT $PBS_JOBID STARTED at `date`"



cp -r $HOME/conversationkg/embeddings_for_the_people $TMPDIR

mkdir $HOME/classifier_BERT

cd $TMPDIR/embeddings_for_the_people/classifier_BERT/

python3 resume_train_classifier.py --save_dir="$HOME/classifier_BERT/checkpoints_20200425-2305/" 


echo "Job resuming train_classifier_BERT $PBS_JOBID ENDED at `date`"