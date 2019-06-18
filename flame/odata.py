#! -*- coding: utf-8 -*-

# Description    Flame Odata class
##
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
##
# Copyright 2018 Manuel Pastor
##
# This file is part of Flame
##
# Flame is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
##
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with Flame.  If not, see <http://www.gnu.org/licenses/>.

import os
import pickle
import json
import numpy as np
from flame.util import utils, get_logger, supress_log

LOG = get_logger(__name__)


class Odata():
    """
    Transforms results into something readable?.

    TODO: Expand Class docstring
    """

    def __init__(self, parameters, conveyor):

        # previous results (eg. object names, mol descriptors) are retained
        self.param = parameters
        self.conveyor = conveyor
        self.format = self.param.getVal('output_format')

    def _output_md(self):
        ''' dumps the molecular descriptors to a TSV file'''

        with open('output_md.tsv', 'w') as fo:

            # Make sure the keys 'var_nam', 'obj_nam', 'xmatrix' actualy exist
            # start writting MD
            if self.conveyor.isKey('var_nam'):
                # header: obj:name + var name

                header = 'name'
                var_nam = self.conveyor.getVal('var_nam')

                for nam in var_nam:
                    header += '\t'+nam
                fo.write(header+'\n')

            if self.conveyor.isKey('xmatrix') and self.conveyor.isKey('obj_nam'):
                # extract obj_name and xmatrix
                xmatrix = self.conveyor.getVal('xmatrix')
                obj_nam = self.conveyor.getVal('obj_nam')

                # iterate for objects
                shape = np.shape(xmatrix)

                if len(shape) > 1:  # 2D matrix (num_obj > 1)
                    for x in range(shape[0]):
                        line = obj_nam[x]
                        for y in range(shape[1]):
                            line += '\t'+str(xmatrix[x, y])
                        fo.write(line+'\n')

                else:             # 1D matrix (num_obj = 1)
                    line = obj_nam[0]
                    for y in range(shape[0]):
                        line += '\t'+str(xmatrix[y])
                    fo.write(line+'\n')

        LOG.info('Molecular descriptors dumped into output_md.tsv')

    def print_result (self, val):
        ''' Prints in the console the content of results given as an 
        argument (val) in a human-readable format 
        '''
        if len(val) < 3:
            print('       ',val)
        else:
            v3 = val[2]
            try:
                v3 = float("{0:.4f}".format(v3))
            except:
                pass

            print(f'       {val[0]} ( {val[1]} ) : {v3}')

    def run_learn(self):
        '''Process the results of learn,
        usually a report on the model quality
        '''
        # the ouput generated by the building are:
        # 
        # 1. results.pkl
        # 2. console output
        # 3. molecular descriptors file in TSV format [optional]
        # 4. results file in TSV format [optional]
        # 
        # (note) no JSON file is produced because this was already
        # implemented in manage.py. Call action_info (model, version, output='JSON')

        ####
        # 1. results.pkl
        ####
        # info_pkl_path = os.path.join(self.param.getVal('model_path'), 'info.pkl')
        # LOG.debug('saving model information to:{}'.format(info_pkl_path))
        # with open(info_pkl_path, 'wb') as handle:
        #     pickle.dump(self.results['model_build_info'], handle)
        #     pickle.dump(self.results['model_valid_info'], handle)

        results_pkl_path = os.path.join(self.param.getVal('model_path'), 'results.pkl')
        LOG.debug('saving model results to:{}'.format(results_pkl_path))
        with open(results_pkl_path, 'wb') as handle:
            self.conveyor.save(handle)
            #pickle.dump(self.conveyor, handle)

        ####
        # 2. console output
        ####

        if self.conveyor.isKey('model_build_info'):
            for val in self.conveyor.getVal('model_build_info'):
                self.print_result (val)

        if self.conveyor.isKey('model_valid_info'):
            for val in self.conveyor.getVal('model_valid_info'):
                self.print_result (val)

        ###
        # 3. molecular descriptors file in TSV format [optional]
        ###
        if self.param.getVal('output_md'):
            self._output_md()

        ###
        # 4. results file in TSV format [optional]
        ### 
        if 'TSV' in self.format:
            LOG.info('writting results to TSV file "output.tsv"')

            # label and smiles
            key_list = ['obj_nam']
            if self.conveyor.isKey('SMILES'):
                key_list.append('SMILES')

            # main result
            key_list += self.conveyor.getMain()

            # add all object type results
            for item in self.conveyor.objectKeys():
                if item not in key_list:
                    key_list.append(item)

            with open('output.tsv', 'w') as fo:
                header = ''
                for label in key_list:
                    header += label+'\t'
                fo.write(header+'\n')

                obj_num = int(self.conveyor.getVal('obj_num'))

                for i in range(obj_num):
                    line = ''
                    for key in key_list:

                        val_array = self.conveyor.getVal(key)

                        if i >= len(val_array):
                            val = None
                        else:
                            val = val_array[i]

                        if val is None:
                            line += '-'
                        else:
                            if isinstance(val, float):
                                line += "%.4f" % val
                            else:
                                line += str(val)
                        line += '\t'
                    fo.write(line+'\n')

        return True, 'building OK'

    def run_apply(self):
        ''' Process the results of apply.
            The ouput generated by the prediction are:       
            1. console output
            2. molecular descriptors file in TSV format [optional]
            3. results file in TSV format [optional]
            4. this function return results in JSON format [optional]
        '''

        if len(self.conveyor.getMain()) == 0:
            self.conveyor.setError('Unable to find main prediction')
            return

        # the ouput generated by the prediction are:
        # 
        # 1. console output
        # 2. molecular descriptors file in TSV format [optional]
        # 3. results file in TSV format [optional]
        # 4. this function return results in JSON format [optional]

        ####
        # 1. console output
        ####
        #print (self.results)

        self.print_result(('obj_num','number of objects',self.conveyor.getVal('obj_num')))

        if self.conveyor.isKey('external-validation'):
            for val in self.conveyor.getVal('external-validation'):
                self.print_result (val)   

        if self.conveyor.isKey('values'):
            for i in range (self.conveyor.getVal('obj_num')):
                print (self.conveyor.getVal('obj_nam')[i], '\t', float("{0:.4f}".format(self.conveyor.getVal('values')[i])))

        ###
        # 2. molecular descriptors file in TSV format [optional]
        ###
        if self.param.getVal('output_md'):
            self._output_md()

        ###
        # 3. results file in TSV format [optional]
        ### 
        if 'TSV' in self.format:
            LOG.info('writting results to TSV file "output.tsv"')
            # label and smiles
            key_list = ['obj_nam']
            if self.conveyor.isKey('SMILES'):
                key_list.append('SMILES')

            # main result
            key_list += self.conveyor.getMain()

            # add all object type results
            # manifest = self.results['manifest']
            # for item in manifest:
            #     if item['dimension'] == 'objs' and item['key'] not in key_list:
            #         key_list.append(item['key'])
            key_obj = self.conveyor.objectKeys()

            for i in key_obj:
                if i not in key_list:
                    key_list.append(i)

            with open('output.tsv', 'w') as fo:
                header = ''
                for label in key_list:
                    header += label+'\t'
                fo.write(header+'\n')

                obj_num = int(self.conveyor.getVal('obj_num'))

                for i in range(obj_num):
                    line = ''
                    for key in key_list:

                        if i >= len(self.conveyor.getVal(key)):
                            val = None
                        else:
                            val = self.conveyor.getVal(key)[i]

                        if val is None:
                            line += '-'
                        else:
                            if isinstance(val, float):
                                line += "%.4f" % val
                            else:
                                line += str(val)
                        line += '\t'
                    fo.write(line+'\n')

        # the function returns "True, output". output can be empty or a JSON
        output = ''

        ###
        # 4. this function return results in JSON format [optional]
        ###
        # returns a JSON with the prediction results
        if 'JSON' in self.format:
            output = self.conveyor.getJSON()

        # Save conveyor from prediction just if confidential is False

        if not self.param.getVal('confidential'):
            results_pkl_path = os.path.join(self.param.getVal('model_path'),
                                            'prediction-results.pkl')
            LOG.debug('saving model results to:{}'.format(results_pkl_path))
            with open(results_pkl_path, 'wb') as handle:
                self.conveyor.save(handle)

        return True, output


    def run_slearn(self):
        '''Process the results of slearn,
        usually a report on the space creation 
        '''
        # the ouput generated by the building are:
        # 
        # 1. results.pkl
        # 2. console output
        # 3. molecular descriptors file in TSV format [optional]
        # 4. results file in TSV format [optional]
        # 
        # (note) no JSON file is produced because this was already
        # implemented in manage.py. Call action_info (model, version, output='JSON')

        ####
        # 1. results.pkl
        ####
        # info_pkl_path = os.path.join(self.param.getVal('model_path'), 'info.pkl')
        # LOG.debug('saving model information to:{}'.format(info_pkl_path))
        # with open(info_pkl_path, 'wb') as handle:
        #     pickle.dump(self.results['model_build_info'], handle)
        #     pickle.dump(self.results['model_valid_info'], handle)

        results_pkl_path = os.path.join(self.param.getVal('model_path'), 'results.pkl')
        LOG.debug('saving space results to:{}'.format(results_pkl_path))
        with open(results_pkl_path, 'wb') as handle:
            self.conveyor.save(handle)
            #pickle.dump(self.conveyor, handle)

        ####
        # 2. console output
        ####

        # if self.conveyor.isKey('model_build_info'):
        #     for val in self.conveyor.getVal('model_build_info'):
        #         self.print_result (val)

        # if self.conveyor.isKey('model_valid_info'):
        #     for val in self.conveyor.getVal('model_valid_info'):
        #         self.print_result (val)

        return True, 'space creation OK'


    def run_error(self):
        '''Formats error messages
        sending only the error and the error source
        '''
        LOG.debug('formating errors in results')

        error_json = {}
        if self.conveyor.getError():
            error_json['error'] = self.conveyor.getErrorMessage()

        if self.conveyor.getWarning():
            error_json['warning'] = self.conveyor.getWarningMessage()

        # write to console
        for key, value in error_json.items():
            LOG.error (value)

        # dump to error.tsv file
        if 'TSV' in self.format:
            LOG.info('Dumping errors into errors.tsv')
            with open('error.tsv', 'w') as fo:
                for key, value in error_json.items():
                    fo.write(key+'\t'+value+'\n')

        output = 'undefined errors'
        
        # replace the undefined error message for a more informative JSON  
        if 'JSON' in self.format:
            LOG.info('Dumping errors into JSON')
            output = json.dumps(error_json)

        return False, output

    def run(self):
        '''Formats the results produced by "learn" or "apply"'''

        origin = self.conveyor.getOrigin()

        if self.conveyor.getError():
            success, results = self.run_error()

        elif origin == 'learn':
            success, results = self.run_learn()

        elif origin == 'apply':
            success, results = self.run_apply()

        elif origin == 'slearn':
            success, results = self.run_slearn()

        else:
            return False, 'error'

        return success, results
