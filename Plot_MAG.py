#! /user/bin/evn python
# -*- coding:utf8 -*-

"""
Plot_MAG
======
A class for something.
@author: Guoxiu He
"""

import os
import random
import sys
import argparse
import datetime
sys.path.insert(0, './')
sys.path.insert(0, '../')
from Explore_MAG import Explore_MAG
import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np


class Plot_MAG(Explore_MAG):
    def __init__(self):
        super(Plot_MAG, self).__init__()
        self.paper_features_path = self.tmp_mag_root + 'paper_features/'

    # Figure 2 (a)
    # We plot Figure 2 (a) via Gephi based on Tmp_MAG/cluster/node.xlsx and Tmp_MAG/cluster/relation.xlsx.

    # Figure 2 (b)
    # Data: Tmp_MAG/year_count_accum.json
    def plot_year_count_accum(self):
        with open(self.tmp_mag_root + 'year_count_accum.json', 'r') as fp:
            year_count_accum_dict = json.load(fp)

        year_list = list(range(1960, 2016))
        count_list = []
        for year in year_list:
            count_list.append(year_count_accum_dict[str(year)])
        count_list = np.array(count_list) / 1000000

        plt.figure(figsize=(10, 4))
        plt.vlines(x=2000, ymin=min(count_list), ymax=max(count_list), color='white', linewidth=0)
        sns.lineplot(x=year_list, y=count_list, linewidth=4)
        plt.grid(axis='y')
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18, rotation=90)
        plt.locator_params(nbins=4, axis='y')
        if not os.path.exists('./imgs_mag/year_count/'):
            os.mkdir('./imgs_mag/year_count/')
        plt.savefig('./imgs_mag/year_count/year_count_accum.pdf', bbox_inches='tight')

    # Figure 2 (c) and (d)
    # Data: Tmp_MAG/count/#fos_1_cit_year_count.json and Tmp_MAG/count/#fos_1_cit_count.json
    def plot_all_count(self, from_level=1):
        if os.path.exists(self.tmp_mag_root + 'cit_fos_year_count.json'):
            with open(self.tmp_mag_root + 'cit_fos_year_count.json', 'r') as fp:
                cit_dict = json.load(fp)
        else:
            cit_dict = {}
            for path in os.listdir(self.tmp_mag_root + 'count/'):
                if '_{}_cit_year_count'.format(from_level) in path:
                    print(path)
                    display_name = '_'.join(path.strip().split('_')[:-4])
                    if display_name == 'All':
                        continue
                    with open(self.tmp_mag_root + 'count/' + path, 'r') as fp:
                        cit_year_count = json.load(fp)
                        for cit, year_count in cit_year_count.items():
                            sorted_year_count = sorted(year_count.items(), key=lambda x: x[0], reverse=False)
                            year_list = []
                            count_list = []
                            for year, count in sorted_year_count:
                                year_list.append(int(year))
                                count_list.append(int(count))
                            if cit not in cit_dict:
                                cit_dict[cit] = {}
                            cit_dict[cit][display_name] = [sum(count_list),
                                                           [year_list, list(np.array(count_list)/1000000)]]

                if '_{}_year_count'.format(from_level) in path:
                    print(path)
                    display_name = '_'.join(path.strip().split('_')[:-3])
                    if display_name == 'All':
                        continue
                    with open(self.tmp_mag_root + 'count/' + path, 'r') as fp:
                        year_count = json.load(fp)
                        sorted_year_count = sorted(year_count.items(), key=lambda x: x[0], reverse=False)
                        year_list = []
                        count_list = []
                        for year, count in sorted_year_count:
                            year_list.append(int(year))
                            count_list.append(int(count))
                        if 'all' not in cit_dict:
                            cit_dict['all'] = {}
                        cit_dict['all'][display_name] = [sum(count_list),
                                                         [year_list, list(np.array(count_list) / 1000000)]]

            with open(self.tmp_mag_root + 'cit_fos_year_count.json', 'w') as fw:
                json.dump(cit_dict, fw)

        linestyles = ['-', '--', '-.', ':']
        markers = ['.', ',', 'o', 'v']
        combines = []
        for linestyle in linestyles:
            for marker in markers:
                combines.append((linestyle, marker))
        combines = combines * 2
        for cit, info in cit_dict.items():
            sorted_info = sorted(cit_dict['all'].items(), key=lambda x: x[1][0], reverse=True)
            if cit == 'all':
                plt.figure(figsize=(10, 4))
            else:
                plt.figure(figsize=(float(8/3), 4))

            plt.vlines(x=2000, ymin=0, ymax=1, color='white', linewidth=0)
            for _id, (display_name, _) in enumerate(sorted_info):
                year_count = info[display_name]
                print(year_count[1][0])
                print(year_count[1][1])
                sns.lineplot(x=year_count[1][0], y=year_count[1][1],
                             label=' '.join(display_name.split('_')),
                             linestyle=combines[_id][0], marker=combines[_id][1],
                             linewidth=1, markersize=3.5)
            plt.grid(axis='y')
            if cit == 'all':
                plt.ylim(top=1)
            else:
                plt.ylim(top=0.6)
            if cit == 'all':
                plt.legend(ncol=2, prop={'size': 11})
            else:
                plt.legend([],[], frameon=False)
            if cit == 'cit_0':
                plt.figtext(0.165, 0.83, r'non-cited papers', fontsize=14)
                plt.figtext(0.165, 0.77, r'(citations$=$0)', fontsize=14)
            elif cit == 'cit_0_10':
                plt.figtext(0.165, 0.83, r'cited papers', fontsize=14)
                plt.figtext(0.165, 0.77, r'(1$\leq$citations$<$10)', fontsize=14)
            elif cit == 'cit_10':
                plt.figtext(0.165, 0.83, r'well-cited papers', fontsize=14)
                plt.figtext(0.165, 0.77, r'(citations$\geq$10)', fontsize=14)
            else:
                pass
            plt.xticks(fontsize=18)
            plt.yticks(fontsize=18, rotation=90)
            plt.locator_params(nbins=4, axis='y')
            if not os.path.exists('./imgs_mag/year_count/'):
                os.mkdir('./imgs_mag/year_count/')
            plt.savefig('./imgs_mag/year_count/year_count_{}.pdf'.format(cit), bbox_inches='tight')

    # Figure 3 (a) and (b)
    # Data: Tmp_MAG/fos_ref_num/*, Tmp_MAG/fos_ref_age/*, and Tmp_MAG/fos_ref_stata/*
    def plot_ref_age_num(self, key=0):
        cit_phase_dict = {'cit_0': 'citation=0', 'cit_0_10': '0<citation<10', 'cit_10': 'citation>=10'}

        for path in os.listdir(self.tmp_mag_root + 'fos_ref_age/'):
            display_name = '_'.join(path.strip().split('_')[:-5])
            ref_age_path = self.tmp_mag_root + 'fos_ref_age/' + path
            ref_num_path = self.tmp_mag_root + 'fos_ref_num/{}_fos_1_paper_ref_num.json'.format(display_name)
            ref_stata_path = self.tmp_mag_root + 'fos_ref_stata/{}_fos_1_paper_ref_stata.json'.format(display_name)

            with open(ref_age_path, 'r') as fp:
                ref_age_dict = json.load(fp)
            with open(ref_num_path, 'r') as fp:
                ref_num_dict = json.load(fp)
            with open(ref_stata_path, 'r') as fp:
                ref_stata_dict = json.load(fp)

            num_dict = {}
            max_dict, var_start_dict, price_index_1_dict, min_1_dict = {}, {}, {}, {}

            for cit_phase, year_age_dict in ref_age_dict.items():
                sorted_year_age_list = sorted(year_age_dict.items(), key=lambda x: int(x[0]))
                year_num_dict = ref_num_dict[cit_phase]
                year_stata_dict = ref_stata_dict[cit_phase]
                num_list, max_list, min_1_list, price_index_1_list, var_start_list = [], [], [], [], []
                for year, age_list in sorted_year_age_list:
                    num_list.append(float(year_num_dict[year][key]))
                    max_list.append(float(age_list[1][key]))
                    var_start_list.append(float(year_stata_dict[year][7][key]))
                    price_index_1_list.append(float(year_stata_dict[year][5][key]))
                    min_1_list.append(float(year_stata_dict[year][4][key]))

                num_dict[cit_phase] = num_list
                max_dict[cit_phase] = max_list
                var_start_dict[cit_phase] = var_start_list
                price_index_1_dict[cit_phase] = price_index_1_list
                min_1_dict[cit_phase] = min_1_list

            plot_dict = {
                'ref_num': num_dict,
                'ref_age_max': max_dict,
                'ref_var_start': var_start_dict,
                'ref_price_index_1': price_index_1_dict,
                'ref_min_1': min_1_dict,
            }

            for plot_name, plot_data in plot_dict.items():

                if plot_name == 'ref_num':
                    plt.figure(figsize=(3, 4))
                else:
                    plt.figure(figsize=(float(8/4), 4))
                x = list(range(1960, 2016))
                sns.color_palette("Paired")
                sns.lineplot(x=x, y=plot_data['cit_10'], label=cit_phase_dict['cit_10'], linewidth=4, color='#1D458F')
                sns.lineplot(x=x, y=plot_data['cit_0_10'], label=cit_phase_dict['cit_0_10'], linewidth=4, color='#B62226')
                sns.lineplot(x=x, y=plot_data['cit_0'], label=cit_phase_dict['cit_0'], linewidth=4, color='#BD832E')
                plt.fill_between(x=x, y1=plot_data['cit_0_10'], y2=plot_data['cit_0'], color='#F0E7D7')
                plt.fill_between(x=x, y1=plot_data['cit_10'], y2=plot_data['cit_0_10'], color='#97C6E7')
                plt.grid(axis='y')
                if plot_name == 'ref_num':
                    if display_name == 'All':
                        plt.ylim(top=42)
                    plt.legend(ncol=1, prop={'size': 14}, loc='upper left')
                else:
                    plt.legend([],[], frameon=False)
                if plot_name == 'ref_age_max':
                    plt.figtext(0.18, 0.83, r'maximum', fontsize=14)
                if plot_name == 'ref_var_start':
                    if display_name == 'All':
                        plt.ylim(top=0.75)
                    plt.figtext(0.18, 0.83, r'variation', fontsize=14)
                if plot_name == 'ref_price_index_1':
                    if display_name == 'All':
                        plt.ylim(top=0.225)
                    plt.figtext(0.18, 0.83, r'ratio of latest', fontsize=14)
                if plot_name == 'ref_min_1':
                    plt.figtext(0.18, 0.83, r'number of', fontsize=14)
                    plt.figtext(0.18, 0.77, r'latest', fontsize=14)
                if plot_name != 'ref_num':
                    plt.xticks([1970, 2005], fontsize=18)
                else:
                    plt.xticks(fontsize=18)
                plt.yticks(fontsize=18, rotation=90)
                plt.locator_params(nbins=4, axis='y')
                if not os.path.exists('./imgs_mag/{}/'.format(plot_name)):
                    os.mkdir('./imgs_mag/{}/'.format(plot_name))
                plt.savefig('./imgs_mag/{}/{}_{}_{}.pdf'.format(plot_name, plot_name, display_name, key), bbox_inches='tight')
                plt.close()

    # Figure 3 (c)
    # Data: Tmp_MAG/fos_ref_cit_features/*
    def plot_ref_cit(self, key=0):
        cit_phase_dict = {'cit_0': 'citation=0', 'cit_0_10': '0<citation<10', 'cit_10': 'citation>=10'}

        for path in os.listdir(self.tmp_mag_root + 'fos_ref_cit_features/'):
            display_name = '_'.join(path.strip().split('_')[:-5])
            ref_cit_features_path = self.tmp_mag_root + 'fos_ref_cit_features/' + path

            with open(ref_cit_features_path, 'r') as fp:
                ref_cit_features_dict = json.load(fp)

            max_dict, var_start_dict, price_index_0_dict, min_0_dict, median_potential_dict = \
                {}, {}, {}, {}, {}

            for cit_phase, year_cit_features_dict in ref_cit_features_dict.items():
                sorted_year_cit_features_dict = sorted(year_cit_features_dict.items(), key=lambda x: int(x[0]))
                max_list, var_start_list, price_index_0_list, min_0_list, median_potential_list = \
                    [], [], [], [], []
                for year, cit_features_list in sorted_year_cit_features_dict:
                    max_list.append(float(cit_features_list[1][key]))
                    var_start_list.append(float(cit_features_list[7][key]))
                    price_index_0_list.append(float(cit_features_list[15][key]))
                    min_0_list.append(float(cit_features_list[14][key]))
                    median_potential_list.append(float(cit_features_list[16][key]))

                max_dict[cit_phase] = max_list
                var_start_dict[cit_phase] = var_start_list
                price_index_0_dict[cit_phase] = price_index_0_list
                min_0_dict[cit_phase] = min_0_list
                median_potential_dict[cit_phase] = median_potential_list

            plot_dict = {
                'ref_cit_max': max_dict,
                'ref_cit_var_start': var_start_dict,
                'ref_cit_price_index_0': price_index_0_dict,
                'ref_cit_min_0': min_0_dict,
                'ref_cit_median_potential': median_potential_dict
            }

            for plot_name, plot_data in plot_dict.items():
                plt.figure(figsize=(float(8/4), 4))
                x = list(range(1960, 2016))

                sns.lineplot(x=x, y=plot_data['cit_10'], label=cit_phase_dict['cit_10'], linewidth=4, color='#1D458F')
                sns.lineplot(x=x, y=plot_data['cit_0_10'], label=cit_phase_dict['cit_0_10'], linewidth=4, color='#B62226')
                sns.lineplot(x=x, y=plot_data['cit_0'], label=cit_phase_dict['cit_0'], linewidth=4, color='#BD832E')
                plt.fill_between(x=x, y1=plot_data['cit_0_10'], y2=plot_data['cit_0'], color='#F0E7D7')  # #6290b0
                plt.fill_between(x=x, y1=plot_data['cit_10'], y2=plot_data['cit_0_10'], color='#97C6E7')  # #5fa183
                plt.grid(axis='y')
                plt.legend([], [], frameon=False)
                if plot_name == 'ref_cit_max':
                    plt.figtext(0.18, 0.83, r'maximum', fontsize=14)
                if plot_name == 'ref_cit_var_start':
                    plt.figtext(0.18, 0.83, r'variation', fontsize=14)
                if plot_name == 'ref_cit_price_index_0':
                    if 'All' in display_name:
                        plt.ylim(top=0.35)
                    plt.figtext(0.18, 0.83, r'ratio of', fontsize=14)
                    plt.figtext(0.18, 0.77, r'non-cited', fontsize=14)
                if plot_name == 'ref_cit_min_0':
                    if 'All' in display_name:
                        plt.ylim(top=3)
                    plt.figtext(0.18, 0.83, r'number of', fontsize=14)
                    plt.figtext(0.18, 0.77, r'non-cited', fontsize=14)
                if plot_name == 'ref_cit_median_potential':
                    plt.figtext(0.18, 0.83, r'potential of', fontsize=14)
                    plt.figtext(0.18, 0.77, r'non-cited', fontsize=14)
                plt.xticks([1970, 2005], fontsize=18)
                plt.yticks(fontsize=18, rotation=90)
                plt.locator_params(nbins=4, axis='y')
                if not os.path.exists('./imgs_mag/{}/'.format(plot_name)):
                    os.mkdir('./imgs_mag/{}/'.format(plot_name))
                plt.savefig('./imgs_mag/{}/{}_{}_{}.pdf'.format(plot_name, plot_name, display_name, key), bbox_inches='tight')
                plt.close()

    # Figure 4 (a)
    def plot_cause_show_coefficient(self):
        text = '''
        Chemistry	0.051879847	0.032881961
        Materials_science	-0.061874665	0.032696519
        Environmental_science	0.042371097	0.022743819
        Biology	0.300220352	0.014689814
        Engineering	0.186252239	0.010956322
        Physics	0.301201854	-0.010678148
        Mathematics	0.426156606	-0.02194287
        History	0.269208518	-0.024990686
        Geology	0.440498385	-0.037378495
        Political_science	0.476567421	-0.038346459
        Computer_science	0.637164514	-0.044079323
        Medicine	0.638987458	-0.050175753
        Geography	0.66953515	-0.059194348
        Art	0.548719519	-0.061864768
        Population	0.927915151	-0.065679766
        Economics	0.881273671	-0.085958815
        Sociology	0.883893458	-0.08913785
        Philosophy	0.788366368	-0.095948034
        Psychology	1.141464758	-0.124546007
        Business	1.388395543	-0.151359519
        '''

        field_coefficient = {
                'Chemistry': '0.0329',
                'Materials science': '0.0327',
                'Environmental science': '0.0227',
                'Biology': '0.0147',
                'Engineering': '0.0110',
                'Physics': '-0.0107',
                'Mathematics': '-0.0219',
                'History': '-0.0250',
                'Geology': '-0.0374',
                'Political science': '-0.0383',
                'Computer science': '-0.0441',
                'Medicine':	'-0.0502',
                'Geography': '-0.0592',
                'Art': '-0.0619',
                'Population': '-0.0657',
                'Economics': '-0.0860',
                'Sociology': '-0.0891',
                'Philosophy': '-0.0959',
                'Psychology': '-0.1245',
                'Business': '-0.1514'
        }

        linestyles = ['-', '--', '-.', ':']
        markers = ['.', ',', 'o', 'v']
        combines = []
        for linestyle in linestyles:
            for marker in markers:
                combines.append((linestyle, marker))
        combines = combines * 2

        x = np.array([6, 6.5, 7, 7.5, 7.8])
        lines = text.strip().split('\n')
        plt.figure(figsize=(10.5, 4))
        for _id, line in enumerate(lines):
            new_line = line.strip().split()
            if _id == 20:
                sns.lineplot(x=x, y=float(new_line[2]) * x, label=new_line[0], linewidth=4, color='black')
            else:
                sns.lineplot(x=x, y=float(new_line[2]) * x, linestyle=combines[_id][0], marker=combines[_id][1],
                             label='{}: {}'.format(' '.join(new_line[0].strip().split('_')),
                                                  field_coefficient[' '.join(new_line[0].strip().split('_'))]),
                             linewidth=2)
        plt.legend(loc=6, ncol=2, prop={'size': 12})
        plt.xlim(-2, 8)
        plt.xticks([6, 7, 8], fontsize=18)
        plt.yticks(fontsize=18, rotation=90)
        plt.locator_params(nbins=4, axis='y')
        plt.hlines(y=0, xmin=5.9, xmax=8, color='black')
        plt.savefig('./imgs_mag/cause_all_show_coefficient.pdf', bbox_inches='tight')

    # Figure 4 (b)
    def plot_cause_power10(self):
        x = np.arange(0, 3, 0.01)
        y = np.power(10, x)
        plt.figure(figsize=(4, 4))

        sns.lineplot(x=x, y=y, color='#4269a5', linewidth=3)

        plt.vlines(x=1, ymin=-10, ymax=np.power(10, 1), color='#4269a5')
        plt.vlines(x=1.5, ymin=-10, ymax=np.power(10, 1.5), color='#4269a5')
        plt.vlines(x=2, ymin=-10, ymax=np.power(10, 2), color='#4269a5')
        plt.vlines(x=2.5, ymin=-10, ymax=np.power(10, 2.5), color='#4269a5')

        x = np.arange(1, 1.5, 0.01)
        y1 = [np.power(10, 1)] * len(x)
        y2 = [np.power(10, 1.5)] * len(x)
        plt.fill_between(x=x, y1=y1, y2=y2, color='#fea87a')  # , color='#e1ebf3'

        x = np.arange(2, 2.5, 0.01)
        y1 = [np.power(10, 2)] * len(x)
        y2 = [np.power(10, 2.5)] * len(x)
        plt.fill_between(x=x, y1=y1, y2=y2, color='#fd9492')  # , color='#e1ebf3'

        plt.annotate('', xy=(2, np.power(10, 2.5)+31), xycoords='data',
                    xytext=(0.81, 0.345), textcoords='axes fraction',
                    arrowprops=dict(facecolor='black', shrink=0.005),
                    horizontalalignment='right', verticalalignment='top',
                    )

        plt.annotate('', xy=(1.9, np.power(10, 2)), xycoords='data',
                     xytext=(0.629, 0.315), textcoords='axes fraction',
                     arrowprops=dict(facecolor='black', shrink=0.005),
                     horizontalalignment='right', verticalalignment='top',
                     )

        plt.xticks(np.arange(0, 3.5, 0.5))
        plt.xlim(left=-0.2)
        plt.ylim(bottom=-10)
        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18, rotation=90)
        plt.xlabel('number of accumulative publications ($log_{10}$)', fontsize=18)
        plt.ylabel('effect to citation ($log_{10}$)', fontsize=18)
        plt.locator_params(nbins=4, axis='y')
        plt.savefig('./imgs_mag/cause_all_power10.pdf', bbox_inches='tight')


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    parser = argparse.ArgumentParser(description='Process some description.')
    parser.add_argument('--phase', default='test', help='the function name.')

    args = parser.parse_args()
    plot_mag = Plot_MAG()

    if args.phase == 'test':
        print('This is a test process.')

    elif args.phase == 'plot_year_count_accum':
        plot_mag.plot_year_count_accum()
    elif args.phase == 'plot_all_count':
        plot_mag.plot_all_count()

    elif args.phase.strip().split('+')[0] == 'plot_ref_age_num':
        plot_mag.plot_ref_age_num(int(args.phase.strip().split('+')[1]))
    elif args.phase.strip().split('+')[0] == 'plot_ref_cit':
        plot_mag.plot_ref_cit(int(args.phase.strip().split('+')[1]))

    elif args.phase == 'plot_cause_show_coefficient':
        plot_mag.plot_cause_show_coefficient()
    elif args.phase == 'plot_cause_power10':
        plot_mag.plot_cause_power10()

    else:
        print("There is no {} function.".format(args.phase))
    end_time = datetime.datetime.now()
    print('{} takes {} seconds.'.format(args.phase, (end_time - start_time).seconds))

    print('Done Plot_MAG!')
