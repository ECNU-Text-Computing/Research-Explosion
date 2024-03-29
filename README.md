# Research Explosion

[comment]: <> (Research Explosion: More Effort to Climb onto Shoulders of the Giant)

**We recommend everyone primarily follow the README when reproducing our work.**

## Explore_MAG.py

1. Download original MAG dataset into **Dataset/**. Especially, you should make sure there are 
   **Dataset/mag/PaperReferences.txt**, **Dataset/mag/Papers.txt**, <br>
   **Dataset/advanced/FieldOfStudyChildren.txt**, **Dataset/advanced/FieldsOfStudy.txt** and **Dataset/advanced/PaperFieldsOfStudy.txt**.
2. Follow the order of the first part in **run.sh**. All tmp_files are saved in **Tmp_MAG/**. You can also access the **Tmp_MAG/** from the Link: https://pan.baidu.com/s/1QV8oaymoPibPXRSTqsi4Jw?pwd=wmek
3. The following figure presents the flow of the functions and datas.

![Flow of Data Exploration](https://github.com/ECNU-Text-Computing/Research-Explosion/blob/main/imgs/imgs_mag.png)

## Regression_MAG.py

1. Make sure you have 21 files in **Tmp_MAG/paper_features/\*.txt**.
2. Follow the order of the second part in **run.sh**.

## Plot_MAG.py

1. Make sure you have **Tmp_MAG/cluster/node.xlsx** and **Tmp_MAG/cluster/relation.xlsx**. 
   And then use Gephi to plot the clusters of all fields of study.
2. Make sure you have **Tmp_MAG/year_count_accum.json**, <br>
   **Tmp_MAG/count/#fos_1_cit_year_count.json**, **Tmp_MAG/count/#fos_1_cit_count.json**, <br>
   **Tmp_MAG/fos_ref_num/\*.json**, **Tmp_MAG/fos_ref_age/\*.json**, **Tmp_MAG/fos_ref_stata/\*.json**, <br>
   and **Tmp_MAG/fos_ref_cit_features/\*.json**, <br>
   and then run scripts in the third part.

## Cite our work
He Guoxiu, Sun Aixin, Lu Wei. Research Explosion: More Effort to Climb onto Shoulders of the Giant [J]. arXiv preprint arXiv:2307.06506, 2023.
