#!/bin/bash


#SBATCH --job-name=GPT2_x_from_W3CGPT2

#SBATCJ -N 1

#SBATCH --time=100:00:00
#SBATCH --mem=60G

##SBATCH --ntasks=1
##SBATCH --cpus-per-task=6
##SBATCH --ntasks-per-node=1

##SBATCH --partition=gpu_shared
##SBATCH --gres=gpu:1


module load pre2019
module load Python/3.6.3-foss-2017b

module load CUDA/10.0.130 
module load cuDNN/7.3.1-CUDA-10.0.130


echo "Job GPT2_X_from_W3CGPT2 $PBS_JOBID STARTED at `date`"


cp -r $HOME/work/conversationkg/embeddings_for_the_people $TMPDIR

cd $TMPDIR/embeddings_for_the_people/personalised_GPT2/


for n in $(cat "GPT2_X_from_W3CGPT2/auth_names.txt"); do
    trainfile="GPT2_X_from_W3CGPT2/$n.train.raw"
    outdir="GPT2_X_from_W3CGPT2/lm_$n"
    
    rm "$outdir/nothing.txt"
    
    echo "CURRENT AUTHOR: $n"
   

    python3 run_language_modeling.py --train_data_file=$trainfile --model_type=gpt2 --output_dir=$outdir -model_name_or_path=gpt2 --do_train --line_by_line --num_train_epochs=10 --model_name_or_path="W3CGPT2/lm"

    echo "DONE WITH AUTHOR: $n"
done

cp -r $TMPDIR/embeddings_for_the_people/personalised_GPT2/GPT2_X_from_W3CGPT2 $HOME
cp -r $TMPDIR/embeddings_for_the_people/personalised_GPT2/runs $HOME/GPT2_X_from_W3CGPT2


echo "Job W3CGPT2 $PBS_JOBID ENDED at `date`"
