# Research Explosion

[comment]: <> (Research Explosion: More Efforts to Climb onto the Shoulders of Giants, PNAS 2022)

**We recommend everyone primarily follow the README when reproducing our work.**

## Explore MAG

![image](https://github.com/ECNU-Text-Computing/Research-Explosion/blob/main/imgs/data_explore.png)

1. Download original MAG dataset into *Dataset/*.
2. Follow the order of the first part in *run.sh*. The tmp_files are saved in *Tmp_MAG/*.
3. Note that not all generated tmp_files are used in final analysis.

## Regression MAG

1. Make sure you have 21 files in *Tmp_MAG/paper_features/*
2. Follow the order of the second part in *run.sh*.

## Plot MAG

1. Make sure you have *year_count_accum.json* and *cit_fos_year_count.json* or *count/* in *Tmp_MAG/*,
   and then run the first two scripts in the third part.
2. Make sure you have *fos_ref_num/*, *fos_ref_age/*, and *fos_ref_stata/* in *Tmp_MAG/*, 
   and then run the third script in the third part.
3. Make sure you have *fos_ref_cit_features/* in *Tmp_MAG*,
   and then run the forth script in the third part.
4. Run the last two scripts in the third part.
5. Use Gephi to plot the cluster based on node.xlsx and relation.xlsx.