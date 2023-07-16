#! /user/bin/evn python
# -*- coding:utf8 -*-

"""
Explore_MAG
======
A class for something.
@author: Guoxiu He
"""

import os
import random
import argparse
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
import scipy.stats as stats

def gini(array):
    # Calculate the Gini coefficient of a numpy array.
    # based on bottom eq:
    # http://www.statsdirect.com/help/generatedimages/equations/equation154.svg
    # from:
    # http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    # All values are treated equally, arrays must be 1d:
    array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array = array - np.amin(array)
    # Values cannot be 0:
    array = array + 0.0000001
    # Values must be sorted:
    array = np.sort(array)
    # Index per array element:
    index = np.arange(1, array.shape[0] + 1)
    # Number of array elements:
    n = array.shape[0]
    # Gini coefficient:
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array)))


def filter_array(array):
    # Extract middle (0.1, 0.9) of the array.
    array_len = len(array)
    if array_len < 10:
        return array
    else:
        array = np.sort(array)
        start_index = int(array_len * 0.1)
        end_index = int(array_len * 0.9)
        return array[start_index: end_index]


def filter_array_max(array):
    # Extract bottom 0.9 of input array.
    array_len = len(array)
    if array_len < 10:
        return array
    else:
        array = np.sort(array)
        end_index = int(array_len * 0.9)
        return array[: end_index]

# Extract our data from the Microsoft Academic Graph (MAG).
class Explore_MAG(object):
    def __init__(self):
        print('Init...')
        self.data_root = './Dataset/'
        # Download Microsoft Academic Graph (MAG) released in April 26, 2021
        self.mag_root = self.data_root + 'MAG/'
        self.PaperReferences_path = self.mag_root + 'mag/PaperReferences.txt'
        self.Papers_path = self.mag_root + 'mag/Papers.txt'
        self.FieldOfStudyChildren_path = self.mag_root + 'advanced/FieldOfStudyChildren.txt'
        self.FieldsOfStudy_path = self.mag_root + 'advanced/FieldsOfStudy.txt'
        self.PaperFieldsOfStudy_path = self.mag_root + 'advanced/PaperFieldsOfStudy.txt'

        # Extract some important temporary files
        self.tmp_mag_root = './Tmp_MAG/'

    ################################################################################################
    # fundamentals
    ################################################################################################

    # 1
    # Extract detailed information of field of study (fos) from FieldsOfStudy.
    # 从FieldsOfStudy原表中提取fos的细节信息。
    # Get fos_dict, and save it to fos.json
    # 得到fos_dict，保存于fos.json。
    def show_fos(self):
        error_count = 0
        count = 0
        head = ['FieldofStudyId', 'Rank', 'NormalizedName', 'DisplayName', 'MainType',
                'Level', 'PaperCount', 'PaperFamilyCount', 'CitationCount', 'CreateDate']

        info_dict = {}
        NormalizedName_info_dict = {}
        FieldofStudyId_count_didct = {}
        NormalizedName_count_dict = {}
        Level_count_dict = {}
        fos_dict = {}

        with open(self.FieldsOfStudy_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                new_line = line.split('\t')

                FieldofStudyId = new_line[head.index('FieldofStudyId')]
                NormalizedName = new_line[head.index('NormalizedName')]
                DisplayName = new_line[head.index('DisplayName')]
                Level = new_line[head.index('Level')]
                PaperCount = new_line[head.index(('PaperCount'))]

                if FieldofStudyId not in info_dict:
                    info_dict[FieldofStudyId] = line
                else:
                    print("The original line with same FieldofStudyId: {}".format(info_dict[FieldofStudyId]))
                    print("The current line with same FieldofStudyId: {}".format(line))

                if NormalizedName not in NormalizedName_info_dict:
                    NormalizedName_info_dict[NormalizedName] = line
                else:
                    print("The original line with same NormalizedName: {}".format(NormalizedName_info_dict[NormalizedName]))
                    print("The current line with same NormalizedName: {}".format(line))

                if FieldofStudyId not in FieldofStudyId_count_didct:
                    FieldofStudyId_count_didct[FieldofStudyId] = 1
                else:
                    FieldofStudyId_count_didct[FieldofStudyId] += 1

                if NormalizedName not in NormalizedName_count_dict:
                    NormalizedName_count_dict[NormalizedName] = 1
                else:
                    NormalizedName_count_dict[NormalizedName] += 1

                if Level not in Level_count_dict:
                    Level_count_dict[Level] = 1
                else:
                    Level_count_dict[Level] += 1

                if len(new_line) != len(head):
                    print(new_line)
                    error_count += 1

                if FieldofStudyId not in fos_dict:
                    fos_dict[FieldofStudyId] = {"FieldofStudyId": FieldofStudyId,
                                                "NormalizedName": NormalizedName,
                                                "DisplayName": DisplayName,
                                                "Level": Level,
                                                "PaperCount": PaperCount}
                else:
                    print("There is a wrong line: {}".format(line))

        print("There are {} error lines.".format(error_count))
        print("There are {} lines.".format(count))
        print("There are {} info.".format(len(info_dict)))
        print("There are {} fos id.".format(len(FieldofStudyId_count_didct)))
        print("There are {} fos name.".format(len(NormalizedName_count_dict)))
        print(sorted(Level_count_dict.items(), key=lambda x: x[0]))

        with open(self.tmp_mag_root + 'fos.json', 'w') as fw:
            json.dump(fos_dict, fw, ensure_ascii=False)
        print("Done.")

    # 2
    # Extract detailed information of top fos from fos.json, including population.
    # 从fos中获取top_fos的信息，其中将population也作为top fos。
    # Get top_fos_dict, and save it to top_fos.json
    # 得到top_fos_dict，保存至top_fos.json。
    def explore_top_fos(self):
        top_fos_dict = {}
        with open(self.tmp_mag_root + 'fos.json', 'r') as fp:
            fos_dict = json.load(fp)
        for fos_id, info in fos_dict.items():
            level = int(info['Level'])
            if level == 0 or fos_id == '2908647359':
                top_fos_dict[fos_id] = info
        with open(self.tmp_mag_root + 'top_fos.json', 'w') as fw:
            json.dump(top_fos_dict, fw)

        for fos_id, info in top_fos_dict.items():
            print(fos_id, '_'.join(info['DisplayName'].strip().split()), info['PaperCount'])

    # 3
    # Extract father fos for each fos from FieldOfStudyChildren. There is no father fos for level-0 fos.
    # 从FieldOfStudyChildren提取fos的父fos，其中level-0的fos没有父fos，其他层级的fos也可能没有父fos。
    # Therefore, the key of the dict can not be the level-0 fos.
    # 所以key不可能是最顶层的fos。
    # Get fos_fathers_dict, and save it to fos_fathers.json.
    # 得到fos_fathers_dict，保存于fos_fathers.json。
    def show_fos_father(self):
        count = 0
        fos_fathers_dict = {}
        with open(self.FieldOfStudyChildren_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                father, child = line.split('\t')
                if child not in fos_fathers_dict:
                    fos_fathers_dict[child] = [father]
                else:
                    fos_fathers_dict[child].append(father)
        print("There are {} lines.".format(count))
        print("There are {} children.".format(len(fos_fathers_dict)))
        for child, fathers in fos_fathers_dict.items():
            if len(fathers) != len(set(fathers)):
                print(fathers)
        with open(self.tmp_mag_root + 'fos_fathers.json',  'w') as fw:
            json.dump(fos_fathers_dict, fw)
        print("Done.")

    # 4
    # Extract ancestor fos for each fos from fos.json and fos_father.json.
    # Here, we only concern level 1's ancestor
    # 从fos.json和fos_father.json中提取每个fos的top fos，即祖宗fos。from_level=1表明只寻找level 0和level 1的祖父fos。
    # Get fos_ancestor_dict, and save it to fos_1_ancestors.json
    # 获得fos_ancestor_dict，保存至fos_1_ancestors.json。
    def find_ancestor(self, from_level=1):
        with open(self.tmp_mag_root + 'fos.json', 'r') as fp:
            fos_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos_fathers.json',  'r') as fp:
            fos_fathers_dict = json.load(fp)

        def find(fathers):
            # A recurrent function
            # 递归从每个子fos的父fos中找到祖父fos。
            # 输入某个子fos的父fos列表，依次得到父fos的父fos，直致祖父fos（即没有父fos的fos），并返回祖父fos列表。
            ancestor = []
            for father in fathers:
                if father not in fos_fathers_dict:
                    ancestor.append(father)
                else:
                    ancestor += find(fos_fathers_dict[father])
            return ancestor

        fos_ancestor_dict = {}
        for child, fathers in fos_fathers_dict.items():
            level = int(fos_dict[child]["Level"])
            if level <= from_level:
                fos_ancestor_dict[child] = list(set(find(fathers)))

        with open(self.tmp_mag_root + 'fos_{}_ancestors.json'.format(from_level), 'w') as fw:
            json.dump(fos_ancestor_dict, fw)

    # 5
    # Extract publication year and citation count for each paper from Papers.
    # Here, the citation count is counted by 2021. We won't use it in this study.
    # 从Papers表中提取每篇paper发表的年份以及获得的引用。
    # 注意，此时的citation为2021年中收集数据时的数量。仅是中间结果，本文并未直接使用。
    # Get paper_year_dict, and save it to paper_year.json.
    # 得到paper_year_dict，保存至paper_year.json。
    # Get paper_cit_dict, and save it to paper_cit.json.
    # 得到paper_cit_dict，保存至paper_cit.json。
    # Get paper_year_cit_dict, and save it to paper_year_cit.json.
    # 得到paper_year_cit_dict，保存至paper_year_cit.json。
    def explore_paper_year_cit(self):
        count = 0
        error_count = 0
        dup_count = 0
        paper_set = set([])
        paper_year_dict = {}
        paper_cit_dict = {}
        paper_year_cit_dict = {}
        with open(self.Papers_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                new_line = line.split('\t')
                paper_id = new_line[0]
                try:
                    year = int(new_line[7])
                    citation_count = int(new_line[-6])
                except:
                    error_count += 1
                    print(new_line)
                    continue
                paper_year_dict[paper_id] = year
                paper_cit_dict[paper_id] = citation_count
                paper_year_cit_dict[paper_id] = {'year': year, 'cit': citation_count}
                if paper_id in paper_set:
                    dup_count += 1
                else:
                    paper_set.add(paper_id)

        with open(self.tmp_mag_root + 'paper_year.json', 'w') as fw:
            json.dump(paper_year_dict, fw)

        with open(self.tmp_mag_root + 'paper_cit.json', 'w') as fw:
            json.dump(paper_cit_dict, fw)

        with open(self.tmp_mag_root + 'paper_year_cit.json', 'w') as fw:
            json.dump(paper_year_cit_dict, fw)

        print("There are {} lines.".format(count))
        print("There are {} error lines.".format(error_count))
        print("There are {} duplicated lines.".format(dup_count))
        print("Done.")

    # 6
    # Extract paper references for each paper from paper_year.json and PaperReferences.
    # 从paper_year.json和PaperReferences中提取每篇paper的reference list。
    # Get paper_refs_dict, and save it to paper_refs.json.
    # 得到paper_refs_dict，保存至paper_refs.json。
    def explore_paper_ref(self):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        paper_refs_dict = {}
        count = 0
        error_count = 0
        with open(self.PaperReferences_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                paper, ref = line.split('\t')
                if paper not in paper_year_dict or ref not in paper_year_dict:
                    error_count += 1
                    continue
                if paper not in paper_refs_dict:
                    paper_refs_dict[paper] = [ref]
                else:
                    paper_refs_dict[paper].append(ref)
        with open(self.tmp_mag_root + 'paper_refs.json', 'w') as fw:
            json.dump(paper_refs_dict, fw)
        print("There are {} ref links.".format(count))
        print("There are {} error links.".format(error_count))
        print("There are {} papers with references.".format(len(paper_refs_dict)))
        for paper, refs in paper_refs_dict.items():
            if len(refs) != len(set(refs)):
                print(paper, refs)

    # 7
    # Extract reference number of each paper from paper_refs.json.
    # 从paper_refs.json中提取每篇paper的reference数量。
    # Get paper_refs_num_dict, and save it to paper_refs_num.json.
    # 得到paper_refs_num_dict，保存至paper_refs_num.json。
    def explore_paper_ref_num(self):
        with open(self.tmp_mag_root + 'paper_refs.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        paper_refs_num_dict = {}
        for paper, refs in paper_refs_dict.items():
            paper_refs_num_dict[paper] = len(set(refs))

        with open(self.tmp_mag_root + 'paper_refs_num.json', 'w') as fw:
            json.dump(paper_refs_num_dict, fw)

    # 8
    # Extract citation list for each paper from paper_year.json and PaperReferences.
    # 从paper_year.json和PaperReferences中提取每篇paper的citing paper列表。
    # Get paper_citations_dict, and save it to paper_citations.json
    # 得到paper_citations_dict，保存至paper_citations.json。
    def explore_paper_citation(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        count = 0
        error_count = 0
        paper_citations_dict = {}

        with open(self.PaperReferences_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                citation, paper = line.split('\t')
                if paper not in paper_year_dict or citation not in paper_year_dict:
                    error_count += 1
                    continue
                if paper not in paper_citations_dict:
                    paper_citations_dict[paper] = [citation]
                else:
                    paper_citations_dict[paper].append(citation)

        del paper_year_dict

        with open(self.tmp_mag_root + 'paper_citations.json', 'w') as fw:
            json.dump(paper_citations_dict, fw)
        print("There are {} ref links.".format(count))
        print("There are {} papers with citations.".format(len(paper_citations_dict)))

    # 9
    # Extract the citations count each paper has received each year by the end of the year from paper_citations.json and paper_year.json.
    # 从paper_citations.json和paper_year.json提取每篇paper截止每年获得的citation数量。
    # Get paper_citation_year_count_dict, and save it to citation_year_count_#num.json。
    # 得到paper_citation_year_count_dict，然后保存至citation_year_count_#num.json。
    # Due to the plethora of data, the data is stored in batches.
    # 由于数据过多，数据是分批存储的。
    def explore_citation_year_count(self):
        with open(self.tmp_mag_root + 'paper_citations.json', 'r') as fp:
            paper_citations_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        num = 0
        paper_citation_year_count_dict = {}

        for paper, citations in paper_citations_dict.items():
            citation_year_list = [paper_year_dict[citation] for citation in citations]
            sorted_citation_year_list = sorted(citation_year_list)
            year_count_dict = {}
            count = 0
            for year in sorted_citation_year_list:
                count += 1
                year_count_dict[year] = count
            paper_citation_year_count_dict[paper] = year_count_dict
            num += 1
            if num % 10000000 == 0:
                with open(self.tmp_mag_root + 'citation_year_count_{}.json'.format(num), 'w') as fw:
                    json.dump(paper_citation_year_count_dict, fw)
                paper_citation_year_count_dict = {}

        with open(self.tmp_mag_root + 'citation_year_count_{}.json'.format(num), 'w') as fw:
            json.dump(paper_citation_year_count_dict, fw)

    # 10
    # Merge the citation_year_count saved in batches.
    # 将分批保存的citation_year_count合并起来。
    # Get citation_year_count_dict, and save it to citation_year_count.json
    # 获得citation_year_count_dict，保存到citation_year_count.json。
    def explore_combine_citation_year_count(self):
        citation_year_count_dict = {}
        for path in os.listdir(self.tmp_mag_root):
            if 'citation_year_count_' in path:
                with open(self.tmp_mag_root + path, 'r') as fp:
                    tmp_citation_year_count_dict = json.load(fp)
                    print("There are {} papers in {}.".format(len(tmp_citation_year_count_dict), path))
                    citation_year_count_dict = {**citation_year_count_dict, **tmp_citation_year_count_dict}

        with open(self.tmp_mag_root + 'citation_year_count.json', 'w') as fw:
            json.dump(citation_year_count_dict, fw)
        print("There are {} papers in {}.".format(len(citation_year_count_dict), 'citation_year_count.json'))

    ################################################################################################
    # main datasets
    ################################################################################################

    # 11
    # Based on paper_refs_num.json, fos.json, fos_{}_ancestors.json, and PaperFieldsOfStudy,
    # extract ancestor fos for each paper, and filter papers without references at the same time.
    # 提取每篇paper的祖父fos，同时过滤掉没有reference的paper。
    # Get new_paper_fos_ancestors_dict, and save it to paper_fos_1_ancestors.json.
    # 得到new_paper_fos_ancestors_dict，保存至paper_fos_$level_ancestors.json。
    def explore_paper_fos_ancestor(self, from_level=1, from_value=0, need_ref=1):
        with open(self.tmp_mag_root + 'paper_refs_num.json', 'r') as fp:
            paper_refs_num_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos.json', 'r') as fp:
            fos_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos_{}_ancestors.json'.format(from_level), 'r') as fp:
            fos_ancestors_dict = json.load(fp)

        count = 0
        error_count = 0
        paper_fos_ancestors_dict = {}
        with open(self.PaperFieldsOfStudy_path, 'r') as fp:
            while True:
                line = fp.readline().strip()
                if not line:
                    break
                count += 1
                new_line = line.split('\t')
                paper, fos, value = new_line[0], new_line[1], float(new_line[2])
                if need_ref:
                    if (paper not in paper_refs_num_dict) \
                            or (value <= from_value) \
                            or (int(fos_dict[fos]['Level']) > from_level and fos != '2908647359'):
                        continue
                else:
                    if (value <= from_value) \
                            or (int(fos_dict[fos]['Level']) > from_level and fos != '2908647359'):
                        continue

                if fos not in fos_ancestors_dict:
                    if int(fos_dict[fos]['Level']) == 0 or fos == '2908647359':  # fos == population
                        ancestors = {fos}
                    else:
                        error_count += 1
                else:
                    ancestors = set([ancestor for ancestor in fos_ancestors_dict[fos]
                                     if (int(fos_dict[ancestor]['Level']) == 0 or ancestor == '2908647359')])
                if paper not in paper_fos_ancestors_dict:
                    paper_fos_ancestors_dict[paper] = ancestors
                else:
                    paper_fos_ancestors_dict[paper] = paper_fos_ancestors_dict[paper] | ancestors

        new_paper_fos_ancestors_dict = {}
        for paper, ancestors in paper_fos_ancestors_dict.items():
            new_paper_fos_ancestors_dict[paper] = list(ancestors)
        del paper_fos_ancestors_dict

        if need_ref:
            if from_value == 0:
                save_path = self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level)
            else:
                save_path = self.tmp_mag_root + 'paper_fos_{}_ancestors_value_{}.json'.format(from_level, from_value)
        else:
            if from_value == 0:
                save_path = self.tmp_mag_root + 'paper_fos_{}_ancestors_ign_ref.json'.format(from_level)
            else:
                save_path = self.tmp_mag_root + 'paper_fos_{}_ancestors_value_{}_ign_ref.json'.format(from_level, from_value)
        with open(save_path, 'w') as fw:
            json.dump(new_paper_fos_ancestors_dict, fw)

        print("There are {} lines in paper fos file.".format(count))
        print("There are {} level 1+ ancestors.".format(error_count))
        print("There are {} papers with fos.".format(len(new_paper_fos_ancestors_dict)))

        print("Done.")

    # 12
    # Extract fos-paper dict, and get paper list for each fos.
    # 基于paper-fos字典，获得fos-paper字典，即得到每个fos对应的paper列表。
    # Get fos_paper_dict, and save it to fos_1_paper.json.
    # 得到fos_paper_dict，保存至fos_$level_paper.json。
    def explore_fos_paper(self, from_level=1, from_value=0):
        with open(self.tmp_mag_root + 'top_fos.json', 'r') as fp:
            top_fos_dict = json.load(fp)

        fos_paper_dict = {}
        if from_value == 0:
            paper_fos_ancestors_dict_path = self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level)
        else:
            paper_fos_ancestors_dict_path = self.tmp_mag_root + 'paper_fos_{}_ancestors_value_{}.json'.format(from_level, from_value)
        with open(paper_fos_ancestors_dict_path, 'r') as fp:
            paper_fos_ancestors_dict = json.load(fp)
        for paper, foss in paper_fos_ancestors_dict.items():
            for fos in foss:
                if fos not in fos_paper_dict:
                    fos_paper_dict[fos] = [paper]
                else:
                    fos_paper_dict[fos].append(paper)
        if from_value == 0:
            save_path = self.tmp_mag_root + 'fos_{}_paper.json'.format(from_level)
        else:
            save_path = self.tmp_mag_root + 'fos_{}_paper_value_{}.json'.format(from_level, from_value)
        with open(save_path, 'w') as fw:
            json.dump(fos_paper_dict, fw, ensure_ascii=False)

        print("There are {} level 0 foss.".format(len(fos_paper_dict)))
        fos_count_dict = {}
        for fos, papers in fos_paper_dict.items():
            if len(papers) != len(set(papers)):
                print("There is a wrong fos {}.".format(fos))
            else:
                fos_count_dict[fos] = len(papers)
                print(
                    "There are {} papers in fos {} {}.".format(len(papers), top_fos_dict[fos]['DisplayName'], fos))
        sorted_fos_count_dict = sorted(fos_count_dict.items(), key=lambda x: x[1], reverse=True)
        for fos, count in sorted_fos_count_dict:
            print(fos, top_fos_dict[fos]['DisplayName'], count)
        print("Done.")

    # 13
    # Extract the number of papers published in each year from paper_fos_1_ancestors.json and paper_year.json.
    # 从paper_fos_1_ancestors.json和paper_year.json提取每年发表的论文数量。
    # Get year_count_dict, and save it to year_count.json.
    # 获得year_count_dict，并将之保存至year_count.json。
    def explore_year_count(self, from_level=1):
        paper_fos_ancestors_dict_path = self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level)
        with open(paper_fos_ancestors_dict_path, 'r') as fp:
            paper_fos_ancestors_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        count = 0
        error_count = 0
        year_count_dict = {}
        for paper, year in paper_year_dict.items():
            if paper not in paper_fos_ancestors_dict:
                error_count += 1
                continue
            if year not in year_count_dict:
                year_count_dict[year] = 1
            else:
                year_count_dict[year] += 1
            count += 1

        year_count_dict_path = self.tmp_mag_root + 'year_count.json'
        with open(year_count_dict_path, 'w') as fw:
            json.dump(year_count_dict, fw)

        print("There are {} papers.".format(count))
        print("There are {} error papers.".format(error_count))

    # 14
    # Extract citation count for each paper.
    # If bar is given, the citation count is counted in #bar (#bar=5) years
    # 获取每篇paper的citation数量。如果没有指定bar，那么获取2020年来的所有citation数量，否则获取bar内（如5年内）的citation数量。
    # Get paper_citation_features_dict, and save it to paper_citations_features_#bar.json
    # 得到paper_citation_features_dict，保存至paper_citations_features_#bar.json。
    def explore_citation_features(self, bar=None):
        with open(self.tmp_mag_root + 'paper_citations.json', 'r') as fp:
            paper_citations_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'year_count.json', 'r') as fp:
            year_count_dict = json.load(fp)

        count = 0
        error_count = 0
        paper_citation_features_dict = {}

        for paper, citations in paper_citations_dict.items():
            count += 1
            paper_year = paper_year_dict[paper]
            citation_year_list = np.array([paper_year_dict[citation] for citation in citations])
            citation_num = len(citations)
            citation_2020_num = int(np.sum(citation_year_list <= 2020))
            citation_bar_num = int(np.sum(citation_year_list <= paper_year + bar))
            bar_count = 0
            for year in range(paper_year, paper_year + bar + 1):
                if str(year) in year_count_dict:
                    bar_count += year_count_dict[str(year)]
                else:
                    error_count += 1
            citation_rate = citation_bar_num / bar_count
            paper_citation_features_dict[paper] = [citation_num, citation_2020_num, citation_bar_num, citation_rate]

        del paper_citations_dict
        del paper_year_dict
        del year_count_dict

        with open(self.tmp_mag_root + 'paper_citations_features_{}.json'.format(bar), 'w') as fw:
            json.dump(paper_citation_features_dict, fw)

        print("There are {} lines.".format(count))
        print("There are {} error lines.".format(error_count))

    # 15
    # Extract the number of papers published each year from paper_year.json. There is no fos range limitation here.
    # 从paper_year.json中提取每年发表论文的数量。此处没有fos范围的限制。
    # Get year_count_all_dict, and save it to year_count_all.json.
    # 获得year_count_all_dict，然后保存至year_count_all.json。
    def explore_year_count_all(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        count = 0
        year_count_dict = {}
        for paper, year in paper_year_dict.items():
            if year not in year_count_dict:
                year_count_dict[year] = 1
            else:
                year_count_dict[year] += 1
            count += 1

        year_count_dict_path = self.tmp_mag_root + 'year_count_all.json'
        with open(year_count_dict_path, 'w') as fw:
            json.dump(year_count_dict, fw)

        print("There are {} papers.".format(count))

    # 16
    # Extract accumulation number each year from year_count.json.
    # 从year_count.json文件中提取每年累积的论文数量。
    # Get year_count_accum_dict, and save it to year_count_accum.json.
    # 获得year_count_accum_dict，保存至year_count_accum.json。
    def explore_year_count_accum(self):
        with open(self.tmp_mag_root + 'year_count.json', 'r') as fp:
            year_count_dict = json.load(fp)
        sorted_year_count_dict = sorted(year_count_dict.items(), key=lambda x: int(x[0]))
        year_list, count_list = zip(*sorted_year_count_dict)
        new_count_list = []
        for count in count_list:
            if len(new_count_list):
                new_count_list.append(new_count_list[-1] + count)
            else:
                new_count_list.append(count)
        print(year_list)
        print(count_list)
        print(new_count_list)
        year_count_accum_dict = dict(list(zip(year_list, new_count_list)))
        with open(self.tmp_mag_root + 'year_count_accum.json', 'w') as fw:
            json.dump(year_count_accum_dict, fw)

    # 17
    # Filter paper references from paper_refs.json with respect to the paper_fos_1_ancestors.json.
    # 依据paper_fos_1_ancestors.json，从paper_refs.json中过滤不在top fos中的paper。
    # Get new_paper_refs_dict, and save it to paper_refs_only_fos.json.
    # 获得new_paper_refs_dict，然后保存至paper_refs_only_fos.json。
    def explore_paper_refs_respect_fos(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_refs.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level), 'r') as fp:
            paper_fos_ancestors_dict = json.load(fp)

        new_paper_refs_dict = {}
        count = 0
        error_count = 0
        for paper, refs in paper_refs_dict.items():
            if paper in paper_fos_ancestors_dict:
                count += 1
                new_paper_refs_dict[paper] = refs
            else:
                error_count += 1

        del paper_refs_dict
        del paper_fos_ancestors_dict

        print("There are {} lines.".format(count))
        print("There are {} error lines.".format(error_count))

        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'w') as fw:
            json.dump(new_paper_refs_dict, fw)
        print("Save cleaned paper refs dict to {}.".format(self.tmp_mag_root + 'paper_refs_only_fos.json'))

    # 18
    # Extract reference features for each paper from paper_refs_only_fos.json and paper_year.json.
    # 从paper_refs_only_fos.json和paper_year.json中提取paper_ref_features.json。
    # Get paper_ref_features_dict, and save it to paper_ref_features.json.
    # 获得paper_ref_features_dict，然后保存至paper_ref_features.json。
    def explore_ref_features(self):
        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        paper_ref_features_dict = {}
        count = 0
        error_count = 0

        # for paper, refs in paper_refs_dict.items():
        for paper, refs in paper_refs_dict.items():
            count += 1
            paper_year = paper_year_dict[paper]
            ref_year_list = [paper_year_dict[ref] for ref in refs]
            ref_age_list = list(paper_year - np.array(ref_year_list))
            num = len(refs)
            mean = float('{:.2f}'.format(float(np.mean(ref_age_list))))
            median = float(np.median(ref_age_list))
            _max = float(np.max(ref_age_list))
            _min = float(np.min(ref_age_list))
            _range = _max - _min
            std = float('{:.2f}'.format(float(np.std(ref_age_list))))
            bian = float('{:.2f}'.format(std / (mean+0.0000001)))
            _gini = float('{:.2f}'.format(gini(np.array(ref_age_list))))
            price_index = float('{:.2f}'.format(np.sum(np.array(ref_age_list) <= 5) / len(ref_age_list)))
            paper_ref_features_dict[paper] = [num, median, _max, _min, _range, mean, std, bian, _gini, price_index]

        del paper_refs_dict
        del paper_year_dict
        print("There are {} papers.".format(count))
        print("There are {} papers without ref age.".format(error_count))

        with open(self.tmp_mag_root + 'paper_ref_features.json', 'w') as fw:
            json.dump(paper_ref_features_dict, fw)

    # 19
    # Extract reference number for papers with top fos from paper_refs_only_fos.
    # 从paper_refs_only_fos.json中提取每篇paper的reference number。
    # Get paper_ref_num_dict, and save it to paper_ref_num.json.
    # 获取paper_ref_num_dict，然后将之保存至paper_ref_num.json。
    def explore_ref_num(self):
        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        paper_ref_num_dict = {}
        count = 0

        # for paper, refs in paper_refs_dict.items():
        for paper, refs in paper_refs_dict.items():
            count += 1
            paper_ref_num_dict[paper] = len(refs)

        del paper_refs_dict
        print("There are {} papers.".format(count))

        with open(self.tmp_mag_root + 'paper_ref_num.json', 'w') as fw:
            json.dump(paper_ref_num_dict, fw)

    # 20
    # Extract reference age for each paper from paper_refs_only_fos.json and paper_year.json.
    # 从paper_refs_only_fos.json和paper_year.json中提取每篇论文的reference age。
    # Get paper_ref_age_dict, and save it to paper_ref_age.json.
    # 获得paper_ref_age_dict，然后保存至paper_ref_age.json。
    def explore_ref_age(self):
        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        paper_ref_age_dict = {}
        count = 0
        error_count = 0

        # for paper, refs in paper_refs_dict.items():
        for paper, refs in paper_refs_dict.items():
            count += 1
            paper_year = paper_year_dict[paper]
            ref_year_list = [paper_year_dict[ref] for ref in refs]
            ref_age_list = list(paper_year - np.array(ref_year_list))
            median = float(np.median(ref_age_list))
            _max = float(np.max(ref_age_list))
            _min = float(np.min(ref_age_list))
            _range = _max - _min
            mean = float('{:.2f}'.format(np.mean(ref_age_list)))
            std = float('{:.2f}'.format(np.std(ref_age_list)))
            paper_ref_age_dict[paper] = [median, _max, _min, _range, mean, std]

        del paper_refs_dict
        del paper_year_dict
        print("There are {} papers.".format(count))
        print("There are {} papers without ref age.".format(error_count))

        with open(self.tmp_mag_root + 'paper_ref_age.json', 'w') as fw:
            json.dump(paper_ref_age_dict, fw)

    # 21
    # Extract other reference statistics for each paper from paper_refs_only_fos.json and paper_year.json.
    # 从paper_refs_only_fos.json和paper_year.json中提取每篇论文的reference age。
    # Get paper_ref_age_dict, and save it to paper_ref_age.json.
    # 获得paper_ref_stata_dict，然后保存至paper_ref_stata.json。
    def explore_ref_stata(self):
        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        paper_ref_stata_dict = {}
        count = 0
        error_count = 0

        # for paper, refs in paper_refs_dict.items():
        for paper, refs in paper_refs_dict.items():
            count += 1
            # if count > 1000:
            #     break
            paper_year = paper_year_dict[paper]
            ref_year_list = np.array([paper_year_dict[ref] for ref in refs])
            ref_age_list = paper_year - ref_year_list
            _gini = float('{:.2f}'.format(gini(ref_age_list)))
            _gini_mid = float('{:.2f}'.format(gini(filter_array(ref_age_list))))
            min_5 = float(np.sum(ref_age_list <= 5))
            price_index = float('{:.2f}'.format(np.sum(ref_age_list <= 5) / len(ref_age_list)))
            min_1 = float(np.sum(ref_age_list <= 1))
            price_index_1 = float('{:.2f}'.format(np.sum(ref_age_list <= 1) / len(ref_age_list)))
            mean = float('{:.2f}'.format(np.mean(ref_age_list)))
            std = float('{:.2f}'.format(np.std(ref_age_list)))
            variation = float('{:.2f}'.format(std / mean)) if mean != 0 else 0.0
            filtered_array = filter_array_max(ref_age_list)
            mean_start = np.mean(filtered_array)
            std_start = np.std(filtered_array)
            variation_start = float('{:.2f}'.format(std_start / mean_start)) if mean_start != 0 else 0.0

            paper_ref_stata_dict[paper] = [_gini, _gini_mid, min_5, price_index, min_1, price_index_1, variation, variation_start]

        del paper_refs_dict
        del paper_year_dict
        print("There are {} papers.".format(count))
        print("There are {} papers without ref age.".format(error_count))

        with open(self.tmp_mag_root + 'paper_ref_stata.json', 'w') as fw:
            json.dump(paper_ref_stata_dict, fw)

    # 22
    # Split paper_refs_only_fos.json with count.
    # 将paper_refs_only_fos.json按照数量切分。
    # Get tmp_paper_refs_dict, and save it to paper_refs_only_fos_#count.json.
    # 获得tmp_paper_refs_dict，然后保存至paper_refs_only_fos_#count.json。
    def explore_paper_refs_only_fos_by_count(self):
        with open(self.tmp_mag_root + 'paper_refs_only_fos.json', 'r') as fp:
            paper_refs_dict = json.load(fp)
        count = 0
        tmp_paper_refs_dict = {}
        for paper, refs in paper_refs_dict.items():
            tmp_paper_refs_dict[paper] = refs
            count += 1
            if count % 10000000 == 0:
                with open(self.tmp_mag_root + 'paper_refs_only_fos_{}.json'.format(count), 'w') as fw:
                     json.dump(tmp_paper_refs_dict, fw)
                tmp_paper_refs_dict = {}
        with open(self.tmp_mag_root + 'paper_refs_only_fos_{}.json'.format(count), 'w') as fw:
            json.dump(tmp_paper_refs_dict, fw)

    # 23
    # Extract citation count of references for each paper before publication time of this paper
    # from paper_year.json, citation_year_count.json, and paper_refs_only_fos_#num.json.
    # 从paper_year.json，citation_year_count.json 和 paper_refs_only_fos_#num.json中提取每篇paper截止发表前
    # 所列参考文献的引用数量。
    # Get paper_ref_cit_dict, and save it to paper_ref_cit_#num.json.
    # 获得paper_ref_cit_dict，然后保存至paper_ref_cit_#num.json。
    def explore_ref_cit(self):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'citation_year_count.json', 'r') as fp:
            citation_year_count_dict = json.load(fp)

        num = 0
        for path in os.listdir(self.tmp_mag_root):
            if 'paper_refs_only_fos_' in path:
                with open(self.tmp_mag_root + path, 'r') as fp:
                    paper_refs_dict = json.load(fp)
                # for paper, refs in paper_refs_dict.items():
                paper_ref_cit_dict = {}
                for paper, refs in paper_refs_dict.items():
                    paper_year = paper_year_dict[paper]
                    ref_cit_list = []
                    for ref in refs:
                        year_count_dict = citation_year_count_dict[ref]
                        sorted_year_count_dict = sorted(year_count_dict.items(), key=lambda x: int(x[0]))
                        year_count = 0
                        for year, count in sorted_year_count_dict:
                            if int(year) < paper_year:
                                year_count = count
                        ref_cit_list.append(year_count)
                    paper_ref_cit_dict[paper] = ref_cit_list
                    num += 1
                with open(self.tmp_mag_root + 'paper_ref_cit_{}.json'.format(num), 'w') as fw:
                    json.dump(paper_ref_cit_dict, fw)

    # 24
    # Extract potential citation in 5 years of the non-cited reference of one paper after publication
    # from paper_year.json, citation_year_count.json, and paper_refs_only_fos_#num.json.
    # 从paper_year.json，citation_year_count.json，和paper_refs_only_fos_#num.json中提取
    # 每篇paper发表后5年内那些没有被引用过的reference可能获得的citation。
    # Get paper_ref_cit_dict, and save it to paper_ref_potential_cit_#num.json.
    def explore_ref_potential_cit(self):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'citation_year_count.json', 'r') as fp:
            citation_year_count_dict = json.load(fp)

        num = 0
        for path in os.listdir(self.tmp_mag_root):
            if 'paper_refs_only_fos_' in path:
                with open(self.tmp_mag_root + path, 'r') as fp:
                    paper_refs_dict = json.load(fp)
                # for paper, refs in paper_refs_dict.items():
                paper_ref_cit_dict = {}
                for paper, refs in paper_refs_dict.items():
                    paper_year = paper_year_dict[paper]
                    ref_cit_list = []
                    for ref in refs:
                        year_count_dict = citation_year_count_dict[ref]
                        sorted_year_count_dict = sorted(year_count_dict.items(), key=lambda x: int(x[0]))
                        year_count = None
                        turn = True
                        for year, count in sorted_year_count_dict:
                            if int(year) < paper_year:
                                turn = False
                            if turn and int(year) >= paper_year and int(year) <= paper_year + 5:
                                year_count = count
                        if turn and year_count:
                            ref_cit_list.append(year_count)
                    paper_ref_cit_dict[paper] = ref_cit_list
                    num += 1
                with open(self.tmp_mag_root + 'paper_ref_potential_cit_{}.json'.format(num), 'w') as fw:
                    json.dump(paper_ref_cit_dict, fw)

    # 25
    # Merge all paper_ref_cit_#num.json to paper_ref_cit.json
    # 将所有paper_ref_cit_#num.json合并为paper_ref_cit.json
    def explore_combine_ref_cit(self):
        paper_ref_cit_dict = {}
        for path in os.listdir(self.tmp_mag_root):
            if 'paper_ref_cit_' in path:
                with open(self.tmp_mag_root + path, 'r') as fp:
                    tmp_paper_ref_cit_dict = json.load(fp)
                    print("There are {} papers in {}.".format(len(tmp_paper_ref_cit_dict), path))
                    paper_ref_cit_dict = {**paper_ref_cit_dict, **tmp_paper_ref_cit_dict}

        with open(self.tmp_mag_root + 'paper_ref_cit.json', 'w') as fw:
            json.dump(paper_ref_cit_dict, fw)
        print("There are {} papers in {}.".format(len(paper_ref_cit_dict), 'paper_ref_cit.json'))

    # 26
    # Merge all paper_ref_potential_cit_#num.json to paper_ref_potential_cit.json
    # 将所有paper_ref_potential_cit_#num.json合并为paper_ref_potential_cit.json
    def explore_combine_ref_potential_cit(self):
        paper_ref_cit_dict = {}
        for path in os.listdir(self.tmp_mag_root):
            if 'paper_ref_potential_cit_' in path:
                with open(self.tmp_mag_root + path, 'r') as fp:
                    tmp_paper_ref_cit_dict = json.load(fp)
                    print("There are {} papers in {}.".format(len(tmp_paper_ref_cit_dict), path))
                    paper_ref_cit_dict = {**paper_ref_cit_dict, **tmp_paper_ref_cit_dict}

        with open(self.tmp_mag_root + 'paper_ref_potential_cit.json', 'w') as fw:
            json.dump(paper_ref_cit_dict, fw)
        print("There are {} papers in {}.".format(len(paper_ref_cit_dict), 'paper_ref_potential_cit.json'))

    # 27
    # Extract citation features of references for each paper from paper_ref_cit.json and paper_ref_potential_cit.json.
    # 从paper_ref_cit.json和paper_ref_potential_cit.json中提取每篇paper的reference的citation的特征。
    # Get ref_cit_features_dict, and save it to paper_ref_cit_features.json.
    # 获得ref_cit_features_dict，然后保存至paper_ref_cit_features.json。
    def explore_ref_cit_features(self):
        with open(self.tmp_mag_root + 'paper_ref_cit.json', 'r') as fp:
            paper_ref_cit_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_ref_potential_cit.json', 'r') as fp:
            paper_ref_potential_cit_dict = json.load(fp)

        ref_cit_features_dict = {}
        for paper, ref_cit_list in paper_ref_cit_dict.items():
            ref_potential_cit_list = np.array(paper_ref_potential_cit_dict[paper])
            median_potential = float(np.median(ref_potential_cit_list)) if len(ref_potential_cit_list) else None
            ref_cit_list = np.array(ref_cit_list)
            median = float(np.median(ref_cit_list))
            _max = float(np.max(ref_cit_list))
            _min = float(np.min(ref_cit_list))
            _range = _max - _min
            mean = float('{:.2f}'.format(np.mean(ref_cit_list)))
            std = float('{:.2f}'.format(np.std(ref_cit_list)))
            variation = float('{:.2f}'.format(std / mean)) if mean != 0 else 0.0
            filtered_array = filter_array_max(ref_cit_list)
            mean_start = np.mean(filtered_array)
            std_start = np.std(filtered_array)
            variation_start = float('{:.2f}'.format(std_start / mean_start)) if mean_start != 0 else 0.0
            _gini = float('{:.2f}'.format(gini(ref_cit_list)))
            _gini_mid = float('{:.2f}'.format(gini(filter_array(ref_cit_list))))
            min_10 = float(sum(ref_cit_list < 10))
            price_index = float('{:.2f}'.format(sum(ref_cit_list < 10) / len(ref_cit_list)))
            min_5 = float(sum(ref_cit_list <= 5))
            price_index_5 = float('{:.2f}'.format(sum(ref_cit_list <= 5) / len(ref_cit_list)))
            min_0 = float(sum(ref_cit_list == 0))
            price_index_0 = float('{:.2f}'.format(sum(ref_cit_list == 0) / len(ref_cit_list)))
            ref_cit_features_dict[paper] = [median, _max, _min, _range, mean, std,
                                            variation, variation_start, _gini, _gini_mid,
                                            min_10, price_index, min_5, price_index_5, min_0, price_index_0,
                                            median_potential]

        print("There are {} papers with ref cit features.".format(len(ref_cit_features_dict)))

        with open(self.tmp_mag_root + 'paper_ref_cit_features.json', 'w') as fw:
            json.dump(ref_cit_features_dict, fw)

    # 28
    # Split fos_1 papers according to fos and citation count in 5 years from 1960 to 2015 from
    # top_fos.json, paper_year.json, paper_citations_features_5.json, and fos_1_paper.json.
    # 将1960到2015年间fos_1的论文按照fos和5年内的引用数量进行划分。
    # 此处依赖了top_fos.json，paper_year.json，paper_citations_features_5.json，和fos_1_paper.json。
    # Get split_fos_papers, and save it to #fos_fos_1_paper_bar5.json.
    # 获得split_fos_papers，并将之保存至#fos_fos_1_paper_bar5.json。
    def explore_split_fos_papers_with_year_cit(self, from_level=1, bar=5):
        with open(self.tmp_mag_root + 'top_fos.json', 'r') as fp:
            top_fos = json.load(fp)

        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_citations_features_{}.json'.format(bar), 'r') as fp:
            paper_citations_features_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos_{}_paper.json'.format(from_level), 'r') as fp:
            fos_paper_dict = json.load(fp)

        for fos, papers in fos_paper_dict.items():
            display_name = '_'.join(top_fos[fos]['DisplayName'].strip().split())
            count_in_range = 0
            count_out_range = 0
            split_fos_papers = {}
            for paper in papers:
                year = paper_year_dict[paper]
                if 1960 <= year <= 2015:
                # if 1980 <= year <= 2020:
                    count_in_range += 1
                    cit = paper_citations_features_dict[paper][2] if paper in paper_citations_features_dict else 0
                    if cit == 0:
                        if 'cit_0' not in split_fos_papers:
                            split_fos_papers['cit_0'] = {}
                        if year not in split_fos_papers['cit_0']:
                            split_fos_papers['cit_0'][year] = [paper]
                        else:
                            split_fos_papers['cit_0'][year].append(paper)
                    elif cit < 10:
                        if 'cit_0_10' not in split_fos_papers:
                            split_fos_papers['cit_0_10'] = {}
                        if year not in split_fos_papers['cit_0_10']:
                            split_fos_papers['cit_0_10'][year] = [paper]
                        else:
                            split_fos_papers['cit_0_10'][year].append(paper)
                    else:
                        if 'cit_10' not in split_fos_papers:
                            split_fos_papers['cit_10'] = {}
                        if year not in split_fos_papers['cit_10']:
                            split_fos_papers['cit_10'][year] = [paper]
                        else:
                            split_fos_papers['cit_10'][year].append(paper)
                else:
                    count_out_range += 1

            print("{}: There are {} papers in year range.".format(display_name, count_in_range))
            print("{}: There are {} papers out year range.".format(display_name, count_out_range))
            print("{}: There are {} papers totally.".format(display_name, count_in_range + count_out_range))

            with open(self.tmp_mag_root + 'fos_papers/{}_fos_{}_paper_bar{}.json'.format(display_name, from_level, bar), 'w') as fw:
                json.dump(split_fos_papers, fw)

    # 29
    # Split all fos_1 papers according to citation count in 5 years from 1960 to 2015 from
    # paper_year.json, paper_citations_features_5.json, and fos_1_paper.json.
    # 将1960到2015年间所有fos_1的论文5年内的引用数量进行划分。
    # 此处依赖了paper_year.json，paper_citations_features_5.json，和fos_1_paper.json。
    # Get all_fos_papers, and save it to All_fos_1_paper_bar5.json.
    # 获得all_fos_papers，并将之保存至All_fos_1_paper_bar5.json。
    def explore_split_fos_papers_with_year_cit_for_all(self, from_level=1, bar=5):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_citations_features_{}.json'.format(bar), 'r') as fp:
            paper_citations_features_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level), 'r') as fp:
            paper_fos_ancestors_dict = json.load(fp)

        all_fos_papers = {}
        count_in_range = 0
        count_out_range = 0
        for paper, _ in paper_fos_ancestors_dict.items():
            year = paper_year_dict[paper]
            if 1960 <= year <= 2015:
                count_in_range += 1
                cit = paper_citations_features_dict[paper][2] if paper in paper_citations_features_dict else 0
                if cit == 0:
                    if 'cit_0' not in all_fos_papers:
                        all_fos_papers['cit_0'] = {}
                    if year not in all_fos_papers['cit_0']:
                        all_fos_papers['cit_0'][year] = [paper]
                    else:
                        all_fos_papers['cit_0'][year].append(paper)
                elif cit < 10:
                    if 'cit_0_10' not in all_fos_papers:
                        all_fos_papers['cit_0_10'] = {}
                    if year not in all_fos_papers['cit_0_10']:
                        all_fos_papers['cit_0_10'][year] = [paper]
                    else:
                        all_fos_papers['cit_0_10'][year].append(paper)
                else:
                    if 'cit_10' not in all_fos_papers:
                        all_fos_papers['cit_10'] = {}
                    if year not in all_fos_papers['cit_10']:
                        all_fos_papers['cit_10'][year] = [paper]
                    else:
                        all_fos_papers['cit_10'][year].append(paper)
            else:
                count_out_range += 1

        print("{}: There are {} papers in year range.".format('All', count_in_range))
        print("{}: There are {} papers out year range.".format('All', count_out_range))
        print("{}: There are {} papers totally.".format('All', count_in_range + count_out_range))

        with open(self.tmp_mag_root + 'fos_papers/All_fos_{}_paper_bar{}.json'.format(from_level, bar), 'w') as fw:
            json.dump(all_fos_papers, fw)

    # 30
    # Extract the similarity of all fields of study from all files in fos_papers/.
    # 从fos_papers/中提取fos之间的相关度。
    # Get inter_matrix.txt and interdisciplinary.txt.
    # 将获得inter_matrix.txt和interdisciplinary.txt。
    def explore_fos_interdisciplinary(self):
        fos_papers_dict = {}
        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if not path.startswith('All'):
                display_name = path[:-22]
                with open(self.tmp_mag_root + 'fos_papers/' + path, 'r') as fp:
                    data_dict = json.load(fp)
                    data_set = set()
                    for cit_phase, info in data_dict.items():
                        for year, paper_list in info.items():
                            data_set.update(paper_list)
                    fos_papers_dict[display_name] = data_set

        fw1 = open(self.tmp_mag_root + 'inter_matrix.txt', 'w')
        fos_list = []
        with open(self.tmp_mag_root + 'interdisciplinary.txt', 'w') as fw:
            for fos1, paper_set1 in fos_papers_dict.items():
                fos_list.append(fos1)
                ratio_list = []
                for fos2, paper_set2 in fos_papers_dict.items():
                    inter_ratio = len(paper_set1 & paper_set2) / len(paper_set1 | paper_set2)
                    ratio_list.append(inter_ratio)
                    fw.write('{}\t{}\t{}\n'.format(fos1, fos2, inter_ratio))
                fw1.write('\t'.join(list(map(str, ratio_list))) + '\n')
            fw1.write('\t'.join(fos_list) + '\n')
        fw1.close()

    # 31
    # Count how many papers in each citation group and each year from fos_papers/.
    # 从fos_papers/中计算每年每个citation group中的论文数量。
    # Get count/#fos_1_cit_year_count.json and count/#fos_1_year_count.json.
    # 获得count/#fos_1_cit_year_count.json和count/#fos_1_year_count.json。
    def explore_split_count(self, from_level=1):
        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if 'fos_{}_paper'.format(from_level) in path:
                display_name = '_'.join(path.strip().split('_')[:-4])
                with open(self.tmp_mag_root + 'fos_papers/' + path, 'r') as fp:
                    data_dict = json.load(fp)
                    cit_year_count = {}
                    year_count = {}
                    for cit, year_papers in data_dict.items():
                        cit_year_count[cit] = {}
                        for year, papers in year_papers.items():
                            cit_year_count[cit][year] = len(papers)
                            if year not in year_count:
                                year_count[year] = len(papers)
                            else:
                                year_count[year] += len(papers)
                    with open(self.tmp_mag_root + 'count/{}_{}_cit_year_count.json'.format(display_name, from_level), 'w') as fw:
                        json.dump(cit_year_count, fw, ensure_ascii=False)

                    with open(self.tmp_mag_root + 'count/{}_{}_year_count.json'.format(display_name, from_level), 'w') as fw:
                        json.dump(year_count, fw, ensure_ascii=False)

    # 32
    # Show the count.
    # 将上述count打印出来。
    def show_all_count(self, from_level=1):
        for path in os.listdir(self.tmp_mag_root + 'count/'):
            if '_{}_cit_year_count'.format(from_level ) in path:
                display_name = '_'.join(path.strip().split('_')[:-4])
                with open(self.tmp_mag_root + 'count/' + path, 'r') as fp:
                    cit_year_count = json.load(fp)
                    for cit, year_count in cit_year_count.items():
                        sorted_year_count = sorted(year_count.items(), key=lambda x: x[0])
                        year_list = [str(year) for year, _ in sorted_year_count]
                        count_list = [str(count) for _, count in sorted_year_count]
                        print('\t'.join([display_name, cit] + year_list))
                        print('\t'.join([display_name, cit] + count_list))

            if '_{}_year_count'.format(from_level) in path:
                display_name = '_'.join(path.strip().split('_')[:-3])
                with open(self.tmp_mag_root + 'count/' + path, 'r') as fp:
                    year_count = json.load(fp)
                    sorted_year_count = sorted(year_count.items(), key=lambda x: x[0])
                    year_list = [str(year) for year, _ in sorted_year_count]
                    count_list = [str(count) for _, count in sorted_year_count]
                    print('\t'.join([display_name] + year_list))
                    print('\t'.join([display_name] + count_list))

    # 33
    # Extract references for each paper according to fos from paper_refs.json, fos_1_paper.json, and top_fos.json.
    # 从paper_refs.json, fos_1_paper.json，和top_fos.json中提取每个领域中每篇paper的参考文献列表。
    # Get tmp_paper_ref_dict, and save it to #fos_fos_paper_refs.json.
    # 获取tmp_paper_ref_dict，然后将之保存至#fos_fos_paper_refs.json。
    def explore_split_paper_refs(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_refs.json', 'r') as fp:
            paper_refs_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos_{}_paper.json'.format(from_level), 'r') as fp:
            fos_1_paper_dict = json.load(fp)

        with open(self.tmp_mag_root + 'top_fos.json', 'r') as fp:
            top_fos_dict = json.load(fp)

        new_fos_1_paper_dict = {}
        for fos, papers in fos_1_paper_dict.items():
            new_fos_1_paper_dict[fos] = set(papers)
        del fos_1_paper_dict

        for fos, papers in new_fos_1_paper_dict.items():
            display_name = '_'.join(top_fos_dict[fos]['DisplayName'].strip().split())
            tmp_paper_ref_dict = {}
            for paper in paper_refs_dict:
                if paper in papers:
                    tmp_paper_ref_dict[paper] = paper_refs_dict[paper]
            with open(self.tmp_mag_root + 'fos_paper_refs/{}_fos_{}_paper_refs.json'.format(display_name, from_level), 'w') as fw:
                json.dump(tmp_paper_ref_dict, fw)

    # 34
    # Split paper_ref_cit according to fos.
    # 按照fos把paper_ref_cit拆开。
    # Get tmp_paper_ref_cit_dict, and save it to fos_paper_ref_cits/#fos_fos_1_paper_ref_cit.json.
    # 获得tmp_paper_ref_cit_dict，然后将之保存至fos_paper_ref_cits/#fos_fos_1_paper_ref_cit.json。
    def explore_split_paper_ref_cit(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_ref_cit.json', 'r') as fp:
            paper_ref_cit_dict = json.load(fp)

        with open(self.tmp_mag_root + 'fos_{}_paper.json'.format(from_level), 'r') as fp:
            fos_1_paper_dict = json.load(fp)

        with open(self.tmp_mag_root + 'top_fos.json', 'r') as fp:
            top_fos_dict = json.load(fp)

        new_fos_1_paper_dict = {}
        for fos, papers in fos_1_paper_dict.items():
            new_fos_1_paper_dict[fos] = set(papers)
        del fos_1_paper_dict

        for fos, papers in new_fos_1_paper_dict.items():
            display_name = '_'.join(top_fos_dict[fos]['DisplayName'].strip().split())
            tmp_paper_ref_cit_dict = {}
            for paper in paper_ref_cit_dict:
                if paper in papers:
                    tmp_paper_ref_cit_dict[paper] = paper_ref_cit_dict[paper]
            with open(self.tmp_mag_root + 'fos_paper_ref_cits/{}_fos_{}_paper_ref_cit.json'.format(display_name, from_level), 'w') as fw:
                json.dump(tmp_paper_ref_cit_dict, fw)

    # 35
    # Split paper_ref_age according to fos from paper_ref_age.json and fos_papers/.
    # 将paper_ref_age这个文件按照fos分隔开。
    # Get fos_cit_year_ref_age_dict, and save it to fos_ref_age/#fos_ref_age.json or fos_ref_age_list/#fos_ref_age_list.json.
    # 获得fos_cit_year_ref_age_dict，然后将之保存至fos_ref_age/#fos_ref_age.json或fos_ref_age_list/#fos_ref_age_list.json。
    def explore_split_ref_age(self, from_level=1, aggregate=1):
        with open(self.tmp_mag_root + 'paper_ref_age.json', 'r') as fp:
            paper_ref_age_dict = json.load(fp)

        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if 'fos_{}_paper'.format(from_level) in path:
                count = 0
                error_count = 0
                fos_cit_year_ref_age_dict = {}
                with open(self.tmp_mag_root + 'fos_papers/{}'.format(path), 'r') as fp:
                    data_dict = json.load(fp)
                for cit_phase, year_papers_dict in data_dict.items():
                    fos_cit_year_ref_age_dict[cit_phase] = {}
                    for year, papers in year_papers_dict.items():
                        median_list, max_list, min_list, range_list, mean_list, std_list = [], [], [], [], [], []
                        for paper in papers:
                            count += 1
                            if paper in paper_ref_age_dict:
                                age_list = paper_ref_age_dict[paper]
                                median_list.append(age_list[0])
                                max_list.append(age_list[1])
                                min_list.append(age_list[2])
                                range_list.append(age_list[3])
                                mean_list.append(age_list[4])
                                std_list.append(age_list[5])
                            else:
                                error_count += 1

                        if aggregate:
                            fos_cit_year_ref_age_dict[cit_phase][year] = [[float(np.mean(median_list)), float(np.median(median_list))],
                                                                          [float(np.mean(max_list)), float(np.median(max_list))],
                                                                          [float(np.mean(min_list)), float(np.median(min_list))],
                                                                          [float(np.mean(range_list)), float(np.median(range_list))],
                                                                          [float(np.mean(mean_list)), float(np.median(mean_list))],
                                                                          [float(np.mean(std_list)), float(np.median(std_list))]]
                        else:
                            fos_cit_year_ref_age_dict[cit_phase][year] = [median_list, max_list, min_list, range_list, mean_list, std_list]
                print("There are {} papers in {}.".format(count, path))
                print("There are {} papers in {} without ref age.".format(error_count, path))
                if aggregate:
                    with open(self.tmp_mag_root + 'fos_ref_age/{}_ref_age.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_age_dict, fw)
                else:
                    with open(self.tmp_mag_root + 'fos_ref_age_list/{}_ref_age_list.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_age_dict, fw)

    # 36
    # Split paper_ref_num according to fos from paper_ref_num.json and fos_papers/.
    # 将paper_ref_num这个文件按照fos分隔开。
    # Get fos_cit_year_ref_num_dict, and save it to fos_ref_num/#fos_ref_num.json or fos_ref_num_list/#fos_ref_num_list.json.
    # 获得fos_cit_year_ref_num_dict，然后将之保存至fos_ref_num/#fos_ref_num.json或fos_ref_num_list/#fos_ref_num_list.json。
    def explore_split_ref_num(self, from_level=1, aggregate=1):
        with open(self.tmp_mag_root + 'paper_ref_num.json', 'r') as fp:
            paper_ref_num_dict = json.load(fp)

        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if 'fos_{}_paper'.format(from_level) in path:
                count = 0
                error_count = 0
                fos_cit_year_ref_num_dict = {}
                with open(self.tmp_mag_root + 'fos_papers/{}'.format(path), 'r') as fp:
                    data_dict = json.load(fp)
                for cit_phase, year_papers_dict in data_dict.items():
                    fos_cit_year_ref_num_dict[cit_phase] = {}
                    for year, papers in year_papers_dict.items():
                        num_list = []
                        for paper in papers:
                            count += 1
                            if paper in paper_ref_num_dict:
                                num = paper_ref_num_dict[paper]
                                num_list.append(num)
                            else:
                                error_count += 1
                        if aggregate:
                            fos_cit_year_ref_num_dict[cit_phase][year] = [float(np.mean(num_list)), float(np.median(num_list))]
                        else:
                            fos_cit_year_ref_num_dict[cit_phase][year] = [num_list]
                print("There are {} papers in {}.".format(count, path))
                print("There are {} papers in {} without ref age.".format(error_count, path))
                if aggregate:
                    with open(self.tmp_mag_root + 'fos_ref_num/{}_ref_num.json'.format(
                            '_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_num_dict, fw)
                else:
                    with open(self.tmp_mag_root + 'fos_ref_num_list/{}_ref_num_list.json'.format(
                            '_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_num_dict, fw)

    # 37
    # Split paper_ref_stata according to fos from paper_ref_stata.json and fos_papers/.
    # 将paper_ref_stata这个文件按照fos分隔开。
    # Get fos_cit_year_ref_stata_dict, and save it to fos_ref_stata/#fos_ref_stata.json or fos_ref_stata_list/#fos_ref_stata_list.json.
    # 获得fos_cit_year_ref_stata_dict，然后将之保存至fos_ref_stata/#fos_ref_stata.json或fos_ref_stata_list/#fos_ref_stata_list.json。
    def explore_split_ref_stata(self, from_level=1, aggregate=1):
        with open(self.tmp_mag_root + 'paper_ref_stata.json', 'r') as fp:
            paper_ref_stata_dict = json.load(fp)

        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if 'fos_{}_paper'.format(from_level) in path:
                count = 0
                error_count = 0
                fos_cit_year_ref_stata_dict = {}
                with open(self.tmp_mag_root + 'fos_papers/{}'.format(path), 'r') as fp:
                    data_dict = json.load(fp)
                for cit_phase, year_papers_dict in data_dict.items():
                    fos_cit_year_ref_stata_dict[cit_phase] = {}
                    for year, papers in year_papers_dict.items():
                        gini_list, gini_mid_list, min_5_list, price_index_list, min_1_list, price_index_1_list, var_list, var_start_list = [], [], [], [], [], [], [], []
                        for paper in papers:
                            count += 1
                            if paper in paper_ref_stata_dict:
                                stata_list = paper_ref_stata_dict[paper]
                                gini_list.append(stata_list[0])
                                gini_mid_list.append(stata_list[1])
                                min_5_list.append(stata_list[2])
                                price_index_list.append(stata_list[3])
                                min_1_list.append(stata_list[4])
                                price_index_1_list.append(stata_list[5])
                                var_list.append(stata_list[6])
                                var_start_list.append(stata_list[7])
                            else:
                                error_count += 1

                        if aggregate:
                            fos_cit_year_ref_stata_dict[cit_phase][year] = [[float(np.mean(gini_list)), float(np.median(gini_list))],
                                                                            [float(np.mean(gini_mid_list)), float(np.median(gini_mid_list))],
                                                                            [float(np.mean(min_5_list)), float(np.median(min_5_list))],
                                                                            [float(np.mean(price_index_list)), float(np.median(price_index_list))],
                                                                            [float(np.mean(min_1_list)), float(np.median(min_1_list))],
                                                                            [float(np.mean(price_index_1_list)), float(np.median(price_index_1_list))],
                                                                            [float(np.mean(var_list)), float(np.median(var_list))],
                                                                            [float(np.mean(var_start_list)), float(np.median(var_start_list))],
                                                                            ]
                        else:
                            fos_cit_year_ref_stata_dict[cit_phase][year] = [gini_list, gini_mid_list, min_5_list, price_index_list, min_1_list, price_index_1_list, var_list, var_start_list]

                print("There are {} papers in {}.".format(count, path))
                print("There are {} papers in {} without ref age.".format(error_count, path))
                if aggregate:
                    with open(self.tmp_mag_root + 'fos_ref_stata/{}_ref_stata.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_stata_dict, fw)
                else:
                    with open(self.tmp_mag_root + 'fos_ref_stata_list/{}_ref_stata_list.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_stata_dict, fw)

    # 38
    # Split paper_ref_cit_features according to fos from paper_ref_cit_features.json and fos_papers/.
    # 将paper_ref_cit_features这个文件按照fos分隔开。
    # Get fos_cit_year_ref_cit_features_dict, and save it to fos_ref_cit_features/#fos_ref_cit_features.json or fos_ref_cit_features_list/#fos_ref_cit_features_list.json.
    # 获得fos_cit_year_ref_cit_features_dict，然后将之保存至fos_ref_cit_features/#fos_ref_cit_features.json或fos_ref_cit_features_list/#fos_ref_cit_features_list.json。
    def explore_split_ref_cit_features(self, from_level=1, aggregate=1):
        with open(self.tmp_mag_root + 'paper_ref_cit_features.json', 'r') as fp:
            paper_ref_cit_features_dict = json.load(fp)

        for path in os.listdir(self.tmp_mag_root + 'fos_papers/'):
            if 'fos_{}_paper'.format(from_level) in path:
                count = 0
                error_count = 0
                fos_cit_year_ref_cit_features_dict = {}
                with open(self.tmp_mag_root + 'fos_papers/{}'.format(path), 'r') as fp:
                    data_dict = json.load(fp)
                for cit_phase, year_papers_dict in data_dict.items():
                    fos_cit_year_ref_cit_features_dict[cit_phase] = {}
                    for year, papers in year_papers_dict.items():
                        median_list, max_list, min_list, range_list, mean_list, std_list, \
                        var_list, var_start_list, gini_list, gini_mid_list, \
                        min_10_list, price_index_list, min_5_list, price_index_5_list, min_0_list, price_index_0_list, \
                        median_potential_list = \
                            [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
                        for paper in papers:
                            count += 1
                            if paper in paper_ref_cit_features_dict:
                                features_list = paper_ref_cit_features_dict[paper]
                                median_list.append(features_list[0])
                                max_list.append(features_list[1])
                                min_list.append(features_list[2])
                                range_list.append(features_list[3])
                                mean_list.append(features_list[4])
                                std_list.append(features_list[5])
                                var_list.append(features_list[6])
                                var_start_list.append(features_list[7])
                                gini_list.append(features_list[8])
                                gini_mid_list.append(features_list[9])
                                min_10_list.append(features_list[10])
                                price_index_list.append(features_list[11])
                                min_5_list.append(features_list[12])
                                price_index_5_list.append(features_list[13])
                                min_0_list.append(features_list[14])
                                price_index_0_list.append(features_list[15])
                                if features_list[16] is not None:
                                    median_potential_list.append(features_list[16])
                            else:
                                error_count += 1

                        if aggregate:
                            fos_cit_year_ref_cit_features_dict[cit_phase][year] = [[float(np.mean(median_list)), float(np.median(median_list))],
                                                                                   [float(np.mean(max_list)), float(np.median(max_list))],
                                                                                   [float(np.mean(min_list)), float(np.median(min_list))],
                                                                                   [float(np.mean(range_list)), float(np.median(range_list))],
                                                                                   [float(np.mean(mean_list)), float(np.median(mean_list))],
                                                                                   [float(np.mean(std_list)), float(np.median(std_list))],
                                                                                   [float(np.mean(var_list)), float(np.median(var_list))],
                                                                                   [float(np.mean(var_start_list)), float(np.median(var_start_list))],
                                                                                   [float(np.mean(gini_list)), float(np.median(gini_list))],
                                                                                   [float(np.mean(gini_mid_list)), float(np.median(gini_mid_list))],
                                                                                   [float(np.mean(min_10_list)), float(np.median(min_10_list))],
                                                                                   [float(np.mean(price_index_list)), float(np.median(price_index_list))],
                                                                                   [float(np.mean(min_5_list)), float(np.median(min_5_list))],
                                                                                   [float(np.mean(price_index_5_list)), float(np.median(price_index_5_list))],
                                                                                   [float(np.mean(min_0_list)), float(np.median(min_0_list))],
                                                                                   [float(np.mean(price_index_0_list)), float(np.median(price_index_0_list))],
                                                                                   [float(np.mean(median_potential_list)), float(np.median(median_potential_list))]
                                                                                   ]
                        else:
                            fos_cit_year_ref_cit_features_dict[cit_phase][year] = [median_list, max_list, min_list, range_list, mean_list, std_list, var_list, var_start_list, gini_list, gini_mid_list, min_10_list, price_index_list, min_5_list, price_index_5_list, min_0_list, price_index_0_list, median_potential_list]
                print("There are {} papers in {}.".format(count, path))
                print("There are {} papers in {} without ref age.".format(error_count, path))
                if aggregate:
                    with open(self.tmp_mag_root + 'fos_ref_cit_features/{}_ref_cit_features.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_cit_features_dict, fw)
                else:
                    with open(self.tmp_mag_root + 'fos_ref_cit_features_list/{}_ref_cit_features_list.json'.format('_'.join(path.strip().split('_')[:-1])), 'w') as fw:
                        json.dump(fos_cit_year_ref_cit_features_dict, fw)

    # 39
    # Extract all possible variables for regression model
    # from paper_year.json, year_count_accum.json, paper_ref_num.json, paper_ref_age.json,
    # paper_ref_stata.json, paper_ref_cit_features.json.
    # 从paper_year.json，year_count_accum.json，paper_ref_num.json，paper_ref_age.json，
    # paper_ref_stata.json，和paper_ref_cit_features.json中为回归模型提取所有可能的变量。
    # Get paper_features_dict, and save it to paper_features/All_paper_features.json.
    # 获取paper_features_dict，然后将之保存在paper_features/All_paper_features.json。
    def explore_feature_extraction(self):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)

        with open(self.tmp_mag_root + 'year_count_accum.json', 'r') as fp:
            year_count_dict = json.load(fp)

        path_list = ['paper_ref_num', 'paper_ref_age', 'paper_ref_stata', 'paper_ref_cit_features']
        paper_features_dict = {}
        for path in path_list:
            with open(self.tmp_mag_root + '{}.json'.format(path), 'r') as fp:
                data_dict = json.load(fp)
            count = 0
            num = 0
            for paper, info in data_dict.items():
                num += 1
                paper_year = paper_year_dict[paper]
                if 1960 <= paper_year <= 2015:
                    count += 1
                    time_range = 0 if paper_year < 2000 else 1
                    if path == 'paper_ref_num':
                        assert paper not in paper_features_dict
                        paper_features_dict[paper] = [paper_year, time_range, year_count_dict[str(paper_year-1)], info]
                    else:
                        assert paper in paper_features_dict
                        paper_features_dict[paper] += info
            print("There are {} papers in range in {}.".format(count, path))
            print("There are {} papers in total in {}.".format(num, path))

        with open(self.tmp_mag_root + 'paper_citations_features_5.json', 'r') as fp:
            paper_citations_features_5_dict = json.load(fp)
        for paper, _ in paper_features_dict.items():
            if paper not in paper_citations_features_5_dict:
                paper_features_dict[paper].append(0)
            else:
                paper_features_dict[paper].append(paper_citations_features_5_dict[paper][2])

        with open(self.tmp_mag_root + 'paper_features/All_paper_features.json', 'w') as fw:
            json.dump(paper_features_dict, fw)

    # 40
    # Extract all possible variables for each fos.
    # 为每个领域提取所有可能的变量。
    # Besides all files needed in previous function, this part also need paper_fos_1_ancestors.json and top_fos.json.
    # 除了上一个方法的所有文件外，本方法还需要paper_fos_1_ancestors.json和top_fos.json。
    # Get paper_features_dict for each fos, and save it to paper_features/{}_paper_features.json.
    # 获得每个fos的paper_features_dict，然后将之保存至paper_features/#fos_paper_features.json。
    def explore_split_feature_extraction(self, from_level=1):
        with open(self.tmp_mag_root + 'paper_year.json', 'r') as fp:
            paper_year_dict = json.load(fp)
        print("Loaded paper_year_dict.")

        with open(self.tmp_mag_root + 'paper_fos_{}_ancestors.json'.format(from_level), 'r') as fp:
            paper_fos_ancestors_dict = json.load(fp)
        print("Loaded paper_fos_ancestors_dict.")

        with open(self.tmp_mag_root + 'top_fos.json', 'r') as fp:
            top_fos_dict = json.load(fp)
        print("Loaded top_fos_dict.")

        with open(self.tmp_mag_root + 'year_count_accum.json', 'r') as fp:
            year_count_dict = json.load(fp)
        print("Loaded year_count_dict.")

        path_list = ['paper_ref_num', 'paper_ref_age', 'paper_ref_stata', 'paper_ref_cit_features']
        split_paper_features_dict = {}
        for path in path_list:
            with open(self.tmp_mag_root + '{}.json'.format(path), 'r') as fp:
                data_dict = json.load(fp)
            for paper, info in data_dict.items():
                paper_year = paper_year_dict[paper]
                if 1960 <= paper_year <= 2015:
                    paper_foses = paper_fos_ancestors_dict[paper]
                    time_range = 0 if paper_year < 2000 else 1
                    for fos in paper_foses:
                        display_name = '_'.join(top_fos_dict[fos]['DisplayName'].strip().split(' '))
                        if display_name not in split_paper_features_dict:
                            split_paper_features_dict[display_name] = {}
                        if path == 'paper_ref_num':
                            assert paper not in split_paper_features_dict[display_name]
                            split_paper_features_dict[display_name][paper] = [paper_year, time_range, year_count_dict[str(paper_year-1)], info]
                            # split_paper_features_dict[display_name][paper] = [paper_year, time_range, year_count_dict[display_name][str(paper_year)], info]
                        else:
                            assert paper in split_paper_features_dict[display_name]
                            split_paper_features_dict[display_name][paper] += info
            del data_dict
        print("Done split_paper_features_dict.")

        del paper_year_dict
        del year_count_dict
        del paper_fos_ancestors_dict
        del top_fos_dict

        with open(self.tmp_mag_root + 'paper_citations_features_5.json', 'r') as fp:
            paper_citations_features_5_dict = json.load(fp)
        print("Loaded paper_citations_features_5_dict.")

        for fos, paper_features_dict in split_paper_features_dict.items():
            for paper, _ in paper_features_dict.items():
                if paper not in paper_citations_features_5_dict:
                    paper_features_dict[paper].append(0)
                else:
                    paper_features_dict[paper].append(paper_citations_features_5_dict[paper][2])

            with open(self.tmp_mag_root + 'paper_features/{}_paper_features.json'.format(fos), 'w') as fw:
                json.dump(paper_features_dict, fw)

    # 41
    # From json to list
    def explore_feature_json_to_list(self):
        with open(self.tmp_mag_root + 'paper_features/All_paper_features.json', 'r') as fp:
            paper_features_dict = json.load(fp)

        with open(self.tmp_mag_root + 'paper_features/All_paper_features.txt', 'w') as fw:
            for paper, features in paper_features_dict.items():
                features[2] = float('{:.2f}'.format(np.log10(features[2])))
                fw.write('\t'.join([paper] + list(map(str, features))) + '\n')

    # 42
    # From json to list
    def explore_split_feature_json_to_list(self):
        for path in os.listdir(self.tmp_mag_root + 'paper_features/'):
            if 'All' in path:
                continue
            if path.endswith('json'):
                save_path = path.strip().split('.')[0] + '.txt'
                # if os.path.exists(save_path):
                #     continue

                with open(self.tmp_mag_root + 'paper_features/{}'.format(path), 'r') as fp:
                    paper_features_dict = json.load(fp)

                with open(self.tmp_mag_root + 'paper_features/{}'.format(save_path), 'w') as fw:
                    for paper, features in paper_features_dict.items():
                        features[2] = float('{:.2f}'.format(np.log10(features[2])))
                        fw.write('\t'.join([paper] + list(map(str, features))) + '\n')


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    parser = argparse.ArgumentParser(description='Process some description.')
    parser.add_argument('--phase', default='test', help='the function name.')

    Explore_MAGer = Explore_MAG()

    args = parser.parse_args()

    if args.phase == 'test':
        print('This is a test process.')

    # fundamentals

    elif args.phase == 'show_fos':
        Explore_MAGer.show_fos()
    elif args.phase == 'explore_top_fos':
        Explore_MAGer.explore_top_fos()
    elif args.phase == 'show_fos_father':
        Explore_MAGer.show_fos_father()
    elif args.phase.strip().split('+')[0] == 'find_ancestor':
        Explore_MAGer.find_ancestor(int(args.phase.strip().split('+')[1]))
    elif args.phase == 'explore_paper_year_cit':
        Explore_MAGer.explore_paper_year_cit()

    elif args.phase == 'explore_paper_ref':
        Explore_MAGer.explore_paper_ref()
    elif args.phase == 'explore_paper_ref_num':
        Explore_MAGer.explore_paper_ref_num()

    elif args.phase == 'explore_paper_citation':
        Explore_MAGer.explore_paper_citation()
    elif args.phase == 'explore_citation_year_count':
        Explore_MAGer.explore_citation_year_count()
    elif args.phase == 'explore_combine_citation_year_count':
        Explore_MAGer.explore_combine_citation_year_count()

    # main dataset

    elif args.phase.strip().split('+')[0] == 'explore_paper_fos_ancestor':
        Explore_MAGer.explore_paper_fos_ancestor(int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'explore_fos_paper':
        Explore_MAGer.explore_fos_paper(args.phase.strip().split('+')[1])

    elif args.phase.strip().split('+')[0] == 'explore_year_count':
        Explore_MAGer.explore_year_count(int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'explore_citation_features':
        Explore_MAGer.explore_citation_features(int(args.phase.strip().split('+')[1]))

    elif args.phase.strip().split('+')[0] == 'explore_year_count_all':
        Explore_MAGer.explore_year_count_all(int(args.phase.strip().split('+')[1]))
    elif args.phase.strip() == 'explore_year_count_accum':
        Explore_MAGer.explore_year_count_accum()

    elif args.phase == 'explore_paper_refs_respect_fos':
        Explore_MAGer.explore_paper_refs_respect_fos()
    elif args.phase == 'explore_ref_features':
        Explore_MAGer.explore_ref_features()
    elif args.phase == 'explore_ref_num':
        Explore_MAGer.explore_ref_num()
    elif args.phase == 'explore_ref_age':
        Explore_MAGer.explore_ref_age()
    elif args.phase == 'explore_ref_stata':
        Explore_MAGer.explore_ref_stata()
    elif args.phase == 'explore_paper_refs_only_fos_by_count':
        Explore_MAGer.explore_paper_refs_only_fos_by_count()

    elif args.phase == 'explore_ref_cit':
        Explore_MAGer.explore_ref_cit()
    elif args.phase == 'explore_ref_potential_cit':
        Explore_MAGer.explore_ref_potential_cit()
    elif args.phase == 'explore_combine_ref_cit':
        Explore_MAGer.explore_combine_ref_cit()
    elif args.phase == 'explore_combine_ref_potential_cit':
        Explore_MAGer.explore_combine_ref_potential_cit()
    elif args.phase == 'explore_ref_cit_features':
        Explore_MAGer.explore_ref_cit_features()

    elif args.phase.strip().split('+')[0] == 'explore_split_fos_papers_with_year_cit':
        Explore_MAGer.explore_split_fos_papers_with_year_cit(args.phase.strip().split('+')[1])
    elif args.phase.strip().split('+')[0] == 'explore_split_fos_papers_with_year_cit_for_all':
        Explore_MAGer.explore_split_fos_papers_with_year_cit_for_all(args.phase.strip().split('+')[1])

    elif args.phase == 'explore_fos_interdisciplinary':
        Explore_MAGer.explore_fos_interdisciplinary()
    elif args.phase.strip().split('+')[0] == 'explore_split_count':
        Explore_MAGer.explore_split_count(args.phase.strip().split('+')[1])
    elif args.phase.strip().split('+')[0] == 'show_all_count':
        Explore_MAGer.show_all_count(args.phase.strip().split('+')[1])

    elif args.phase == 'explore_split_paper_refs':
        Explore_MAGer.explore_split_paper_refs()
    elif args.phase == 'explore_split_paper_ref_cit':
        Explore_MAGer.explore_split_paper_ref_cit()
    elif args.phase.strip().split('+')[0] == 'explore_split_ref_age':
        Explore_MAGer.explore_split_ref_age(aggregate=int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'explore_split_ref_num':
        Explore_MAGer.explore_split_ref_num(aggregate=int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'explore_split_ref_stata':
        Explore_MAGer.explore_split_ref_stata(aggregate=int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'explore_split_ref_cit_features':
        Explore_MAGer.explore_split_ref_cit_features(aggregate=int(args.phase.strip().split('+')[1]))

    elif args.phase == 'explore_feature_extraction':
        Explore_MAGer.explore_feature_extraction()
    elif args.phase == 'explore_split_feature_extraction':
        Explore_MAGer.explore_split_feature_extraction()
    elif args.phase == 'explore_feature_json_to_list':
        Explore_MAGer.explore_feature_json_to_list()
    elif args.phase == 'explore_split_feature_json_to_list':
        Explore_MAGer.explore_split_feature_json_to_list()

    else:
        print("There is no {} function.".format(args.phase))
    end_time = datetime.datetime.now()
    print('{} takes {} seconds.'.format(args.phase, (end_time - start_time).seconds))

    print('Done Explore_MAG!')
