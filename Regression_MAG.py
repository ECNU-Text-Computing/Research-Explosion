#! /user/bin/evn python
# -*- coding:utf8 -*-

"""
CausalInference_MAG
======
A class for something.
@author: Guoxiu He
"""

import sys
import argparse
import datetime
sys.path.insert(0, './')
sys.path.insert(0, '../')
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

from Explore_MAG import Explore_MAG


class Regression_MAG(Explore_MAG):
    def __init__(self):
        super(Regression_MAG, self).__init__()
        self.paper_features_path = self.tmp_mag_root + 'paper_features/'

    # Fit all publications.
    # Data: Tmp_MAG/paper_features/All_paper_features.txt
    def fit_id_accumulation(self, path):
        df = pd.read_csv(path, sep='\t', header=None)
        df.columns = ['id', 'year', 'period', 'accumulation',
                      'ref_num',
                      'ref_age_median', 'ref_age_max', 'ref_age_min', 'ref_age_range', 'ref_age_mean', 'ref_age_std',
                      'ref_age_gini', 'ref_age_gini_mid', 'ref_age_min_5', 'ref_age_price_index', 'ref_age_min_1', 'ref_age_price_index_1', 'ref_age_var', 'ref_age_var_start',
                      'ref_cit_median', 'ref_cit_max', 'ref_cit_min', 'ref_cit_range', 'ref_cit_mean', 'ref_cit_std', 'ref_cit_var', 'ref_cit_var_start',
                      'ref_cit_gini', 'ref_cit_gini_mid', 'ref_cit_min_10', 'ref_cit_price_index', 'ref_cit_min_5', 'ref_cit_price_index_5', 'ref_cit_min_0', 'ref_cit_price_index_0',
                      'ref_cit_median_potential',
                      'citation_count']
        df['citation_count'] = df.apply(lambda x: np.log10(x.citation_count + 1), axis=1)
        df['ref_cit_max'] = df.apply(lambda x: np.log10(x.ref_cit_max + 1), axis=1)

        df = df.set_index(['id', 'year'])
        print(df.head())
        print(df.info())
        print(set(df['accumulation']))
        est = smf.ols(formula='citation_count ~ '
                              'accumulation + '
                              'ref_num + '
                              'ref_age_max + ref_age_var_start + ref_age_price_index_1 + '
                              'ref_cit_max + ref_cit_var_start + ref_cit_price_index_0', data=df)
        est = est.fit()
        print(est.summary())
        print(est.params)

    # Fit publications for each fos.
    # Data: Tmp_MAG/paper_features/#fos_paper_features.txt
    def fit_id_accumulation_with_fos(self):
        fos_list = ['History', 'Geology', 'Economics', 'Chemistry', 'Philosophy', 'Sociology', 'Materials_science',
                    'Mathematics', 'Biology', 'Computer_science', 'Political_science', 'Engineering', 'Psychology',
                    'Environmental_science', 'Business', 'Physics', 'Medicine', 'Art', 'Population', 'Geography']
        res_list = []
        for fos in fos_list:
            print(fos)
            path = self.paper_features_path + '{}_paper_features.txt'.format(fos)
            df = pd.read_csv(path, sep='\t', header=None)
            df.columns = ['id', 'year', 'period', 'accumulation',
                          'ref_num',
                          'ref_age_median', 'ref_age_max', 'ref_age_min', 'ref_age_range', 'ref_age_mean', 'ref_age_std',
                          'ref_age_gini', 'ref_age_gini_mid', 'ref_age_min_5', 'ref_age_price_index', 'ref_age_min_1', 'ref_age_price_index_1', 'ref_age_var', 'ref_age_var_start',
                          'ref_cit_median', 'ref_cit_max', 'ref_cit_min', 'ref_cit_range', 'ref_cit_mean', 'ref_cit_std', 'ref_cit_var', 'ref_cit_var_start',
                          'ref_cit_gini', 'ref_cit_gini_mid', 'ref_cit_min_10', 'ref_cit_price_index', 'ref_cit_min_5', 'ref_cit_price_index_5', 'ref_cit_min_0', 'ref_cit_price_index_0',
                          'ref_cit_median_potential',
                          'citation_count']
            df['citation_count'] = df.apply(lambda x: np.log10(x.citation_count + 1), axis=1)
            df['ref_cit_max'] = df.apply(lambda x: np.log10(x.ref_cit_max + 1), axis=1)

            df = df.set_index(['id', 'year'])
            print(df.head())
            print(df.info())
            est = smf.ols(formula='citation_count ~ '
                                  'accumulation + '
                                  'ref_num + '
                                  'ref_age_max + ref_age_var_start + ref_age_price_index_1 + '  # ref_age_price_index + 
                                  'ref_cit_max + ref_cit_var_start + ref_cit_price_index_0', data=df)
            est = est.fit()
            print(est.summary())
            print(est.params)
            res_list.append((fos, est.params['Intercept'], est.params['accumulation']))
        for fos, Intercept, growth in res_list:
            print(fos, Intercept, growth)


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    parser = argparse.ArgumentParser(description='Process some description.')
    parser.add_argument('--phase', default='test', help='the function name.')

    args = parser.parse_args()
    regression = Regression_MAG()

    if args.phase == 'test':
        print('This is a test process.')
    elif args.phase == 'fit_id_accumulation':
        data_path = regression.paper_features_path + 'All_paper_features.txt'
        regression.fit_id_accumulation(data_path)
    elif args.phase == 'fit_id_accumulation_with_fos':
        regression.fit_id_accumulation_with_fos()
    else:
        print("There is no {} function.".format(args.phase))
    end_time = datetime.datetime.now()
    print('{} takes {} seconds.'.format(args.phase, (end_time - start_time).seconds))

    print('Done CausalInference_MAG!')
