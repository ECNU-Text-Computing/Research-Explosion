# Research Explosion

[comment]: <> (Research Explosion: More Efforts to Climb onto the Shoulders of Giants, PNAS 2022)

**We recommend everyone primarily follow the README when reproducing our work.**

## Explore MAG

1. Download original MAG dataset into **Dataset/**. Especially, you should make sure there are 
   **Dataset/mag/PaperReferences.txt**, **Dataset/mag/Papers.txt**, <br>
   **Dataset/advanced/FieldOfStudyChildren.txt**, **Dataset/advanced/FieldsOfStudy.txt** and **Dataset/advanced/PaperFieldsOfStudy.txt**.
2. Follow the order of the first part in **run.sh**. All tmp_files are saved in **Tmp_MAG/**.
3. The following figure presents the flow of the functions and datas.

![Flow of Data Exploration](https://github.com/ECNU-Text-Computing/Research-Explosion/blob/main/imgs/imgs_mag.png)

## Regression MAG

1. Make sure you have 21 files in **Tmp_MAG/paper_features/\*.txt**.
2. Follow the order of the second part in **run.sh**.

## Plot MAG

1. Make sure you have **Tmp_MAG/cluster/node.xlsx** and **Tmp_MAG/cluster/relation.xlsx**. 
   And then use Gephi to plot the clusters of all fields of study.
2. Make sure you have **Tmp_MAG/year_count_accum.json**, <br>
   **Tmp_MAG/count/#fos_1_cit_year_count.json**, **Tmp_MAG/count/#fos_1_cit_count.json**, <br>
   **Tmp_MAG/fos_ref_num/\*.json**, **Tmp_MAG/fos_ref_age/\*.json**, **Tmp_MAG/fos_ref_stata/\*.json**, <br>
   and **Tmp_MAG/fos_ref_cit_features/\*.json**, <br>
   and then run scripts in the third part.