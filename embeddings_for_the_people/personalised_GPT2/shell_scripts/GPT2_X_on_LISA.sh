#!/bin/bash


#SBATCH --job-name=GPT2_x

#SBATCH --time=10:00:00
#SBATCH --mem=60G

#SBATCH --nodes=1
#SBATCH --partition=gpu

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --ntasks-per-node=1





##SBATCH --time=10:00:00
##SBATCH --mem=40G

##SBATCH --ntasks=1
##SBATCH --cpus-per-task=6
##SBATCH --ntasks-per-node=1

##SBATCH --partition=gpu_shared
##SBATCH --gres=gpu:2


module load pre2019
module load Python/3.6.3-foss-2017b

module load CUDA/10.0.130 
module load cuDNN/7.3.1-CUDA-10.0.130


echo "Job GPT2_X $PBS_JOBID STARTED at `date`"


cp -r $HOME/conversationkg/embeddings_for_the_people $TMPDIR

cd $TMPDIR/embeddings_for_the_people/personalised_GPT2/


for n in $(cat "GPT2_X/auth_names.txt"); do
    echo "CURRENT AUTHOR: $n"

    trainfile="GPT2_X/$n.train.raw"
    outdir="GPT2_X/lm_$n"
    
    
#     elif [[ ! -d $dir ]]; then
#         echo "$dir already exists but is not a directory" 1>&2
#     fi
    # mkdir -p $trainfile
    # rm "$outdir/nothing.txt"
    
    if [[ ! -e $outdir ]]; then
        mkdir $outdir  

        python3 run_language_modeling.py --train_data_file=$trainfile --model_type=gpt2 --output_dir=$outdir --model_name_or_path=gpt2 --do_train --line_by_line --num_train_epochs=30 --local_rank=4

        echo "DONE WITH AUTHOR: $n"
    
    
    else
        echo "$outdir already exists! skipping this author!"    
    fi
done

cp -r $TMPDIR/embeddings_for_the_people/personalised_GPT2/ $HOME


echo "Job W3CGPT2 $PBS_JOBID ENDED at `date`"



