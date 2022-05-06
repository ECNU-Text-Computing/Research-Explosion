############################################################
# Research Explosion

############################################################
# 1. Explore_MAG.py
############################################################
# fundamentals
python Explore_MAG.py --phase show_fos
python Explore_MAG.py --phase explore_top_fos
python Explore_MAG.py --phase show_fos_father
python Explore_MAG.py --phase find_ancestor+1
python Explore_MAG.py --phase explore_paper_year_cit

python Explore_MAG.py --phase explore_paper_ref
python Explore_MAG.py --phase explore_paper_ref_num

python Explore_MAG.py --phase explore_paper_citation
python Explore_MAG.py --phase explore_citation_year_count
python Explore_MAG.py --phase explore_combine_citation_year_count

# mian dataset
python Explore_MAG.py --phase explore_paper_fos_ancestor+1
python Explore_MAG.py --phase explore_fos_paper+1

python Explore_MAG.py --phase explore_year_count+1
python Explore_MAG.py --phase explore_citation_features+5

python Explore_MAG.py --phase explore_year_count_all+1
python Explore_MAG.py --phase explore_year_count_accum

python Explore_MAG.py --phase explore_paper_refs_respect_fos
python Explore_MAG.py --phase explore_ref_features
python Explore_MAG.py --phase explore_ref_num
python Explore_MAG.py --phase explore_ref_age
python Explore_MAG.py --phase explore_ref_stata
python Explore_MAG.py --phase explore_paper_refs_only_fos_by_count

python Explore_MAG.py --phase explore_ref_cit
python Explore_MAG.py --phase explore_ref_potential_cit
python Explore_MAG.py --phase explore_combine_ref_cit
python Explore_MAG.py --phase explore_combine_ref_potential_cit
python Explore_MAG.py --phase explore_ref_cit_features

python Explore_MAG.py --phase explore_split_fos_papers_with_year_cit+1
python Explore_MAG.py --phase explore_split_fos_papers_with_year_cit_for_all+1

python Explore_MAG.py --phase explore_fos_interdisciplinary
python Explore_MAG.py --phase explore_split_count+1
python Explore_MAG.py --phase show_all_count+1

python Explore_MAG.py --phase explore_split_paper_refs
python Explore_MAG.py --phase explore_split_paper_ref_cit
python Explore_MAG.py --phase explore_split_ref_age+1
python Explore_MAG.py --phase explore_split_ref_num+1
python Explore_MAG.py --phase explore_split_ref_stata+1
python Explore_MAG.py --phase explore_split_ref_cit_features+1

python Explore_MAG.py --phase explore_feature_extraction
python Explore_MAG.py --phase explore_split_feature_extraction
python Explore_MAG.py --phase explore_feature_json_to_list
python Explore_MAG.py --phase explore_split_feature_json_to_list
python Explore_MAG.py --phase explore_split_feature_json_to_list_year

############################################################
# 2. Regression_MAG.py
############################################################

python Regression_MAG.py --phase fit_id_accumulation
python Regression_MAG.py --phase fit_id_accumulation_with_fos

############################################################
# Plot_MAG.py
############################################################

python Plot_MAG.py --phase plot_year_count_accum
python Plot_MAG.py --phase plot_all_count

python Plot_MAG.py --phase plot_ref_age_num+1
python Plot_MAG.py --phase plot_ref_cit+1

python Plot_MAG.py --phase plot_cause_show_coefficient
python Plot_MAG.py --phase plot_cause_power10