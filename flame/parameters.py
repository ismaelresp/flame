#! -*- coding: utf-8 -*-

# Description    Flame Build class
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2018 Manuel Pastor
#
# This file is part of Flame
#
# Flame is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Flame. If not, see <http://www.gnu.org/licenses/>.

import os
import yaml
import json

from flame.util import utils

class Parameters:
    ''' Class storing a large set of parameters defining how a model is built

        These parameters are loaded from a configuration file (typically 
        in yaml format) 

        The version 1 of parameters.yaml is a simple "key-value" python dictionary
        in yaml file

        In version 2 every parameter is a dictionary with keys defining the parameter type, 
        value and providing a human-readable explanation used for the GUI

        This code supports both versions of the parameter file, but the use of version 1
        is deprecated and will not be supported indefinitely 
    '''

    def __init__(self):
        ''' constructor '''
        self.extended = False
        self.param_format = 1
        return

    # def loadDict (self, d):
    #     ''' load the content from a dictionary '''
    #     self.p = d    
    #     return

    def loadYaml (self, model, version):       
        ''' load a set of parameters from the configuration file present 
            at the model directory

            adds some parameters identifying the model and the 
            hash of the configuration file 
        '''

        # obtain the path and the default name of the model parameters
        parameters_file_path = utils.model_path(model, version)
        parameters_file_name = os.path.join (parameters_file_path,
                                            'parameters.yaml')

        # load the main class dictionary (p) from this yaml file
        if not os.path.isfile(parameters_file_name):
            return False

        try:
            with open(parameters_file_name, 'r') as pfile:
                self.p = yaml.load(pfile)
        except Exception as e:
            return False

        # check version of the parameter file
        # no 'version' key mans version < 2.0
        if 'param_format' in self.p:
            self.extended = True
        else:
            self.extended = False
            self.param_format = 1.0

        # add keys for the model and a MD5 hash
        self.setVal('endpoint',model)
        self.setVal('version',version)
        self.setVal('model_path',parameters_file_path)
        self.setVal('md5',utils.md5sum(parameters_file_name))

        return True

    def delta (self, model, version, param_file, iformat='YAML'):
        ''' load a set of parameters from the configuration file present 
            at the model directory

            also, inserts the keys present in the param_file provided, 
            assuming that it contains a YAML-compatible format, like the one
            generated by manage

            adds some parameters identifying the model and the 
            hash of the configuration file 
        '''
        if not self.loadYaml (model, version):
            return False
        
        # parse parameter file assuning it will be in
        # a YAML-compatible format
        try:
            with open(param_file, 'r') as pfile:
                if iformat == 'YAML':
                    newp = yaml.load(pfile)
                elif iformat == 'JSON':
                    newp = json.load(pfile)
        except:
            #print ('parsing of delta failed')
            return False
        
        # update interna dict with keys in the input file (delta)
        black_list = ['param_format','version','model_path','endpoint','md5']
        for key in newp:
            if key not in black_list:

                val = newp[key]

                # YAML define null values as 'None, which are interpreted 
                # as strings
                if val == 'None':
                    val = None

                if isinstance(val ,dict):
                    for inner_key in val:
                        inner_val = val[inner_key]
                        self.setInnerVal(key, inner_key, inner_val)
                        #print ('@delta: adding',key, inner_key, inner_val)
                else:
                    self.setVal(key,val)
                    #print ('@delta: adding',key,val,type(val))

        # dump internal dict to the parameters file
        parameters_file_path = utils.model_path(model, version)
        parameters_file_name = os.path.join (parameters_file_path,
                                            'parameters.yaml')
        try:
            with open(parameters_file_name, 'w') as pfile:
                yaml.dump (self.p, pfile)
        except Exception as e:
            return False

        return True

    @staticmethod
    def saveJSON(self, model, version, input_JSON):
        p = json.load(input_JSON)
        parameters_file_path = utils.model_path(model, version)
        parameters_file_name = os.path.join (parameters_file_path,
                                            'parameters.yaml')
        try:
            with open(parameters_file_name, 'w') as pfile:
                yaml.dump (p, pfile)
        except Exception as e:
            return False

        return True

    def getVal(self, key):
        ''' Return the value of the key parameter or None if it is
            not found in the parameters dictionary
        ''' 
        if not key in self.p:
            return None

        ## compatibility with version 1 (remove)
        if not self.extended:
            return self.p[key]
        ## ---------------------------------------

        if 'value' in self.p[key]:
            return self.p[key]['value']
        return None

    
    def getDict(self, key):
        ''' Return the value of the key parameter or None if it is
            not found in the parameters dictionary
        ''' 
        d = {}
        if not key in self.p:
            return d

        ## compatibility with version 1 (remove)
        if not self.extended:
            return self.p[key]
        ## ---------------------------------------

        element = self.p[key]['value']
        if isinstance(element ,dict):
            # iterate keys and copy to the temp dictionary
            # the key and the content of 'value'
            for k, v in element.items():
                if 'value' in v:
                    d[k] = v['value']
        return d

    
    # def getOldParam(self):
    #     ''' Returns the dictionary with the parameters
    #         This function was defined only for compatibility purposes
    #         during the implementation of this class
    #     '''
    #     return self.p

    def setVal(self, key, value):
        ''' Sets the parameter defined by key to the given value
        '''

        # compatibility with version 1 (remove)
        if not self.extended:
            self.p[key] = value
            return

        # for existing keys, replace the contents of 'value'
        if key in self.p:
            if "value" in self.p[key]:
                if not isinstance(self.p[key]['value'], dict):
                    self.p[key]["value"] = value
                else:
                    for k in value.keys():
                        self.p[key][k] = value[k]

        # for new keys, create a new element with 'value' key
        else:
            self.p[key] = {'value': value}

    def setInnerVal(self, okey, ikey, value):
        ''' Sets the parameter defined by key to the given value
        '''

        if not okey in self.p:
            print ('error1')
            return

        if not "value" in self.p[okey]:
            print ('error2')
            return

        odict = self.p[okey]['value']

        if not isinstance(odict, dict):
            print ('error3')
            return
        
        if not ikey in odict:
            print ('error4')
            return

        if "value" in odict[ikey]:
            odict[ikey]["value"] = value
        else:
            odict[ikey] = {'value': value}


    def appVal(self, key, value):
        ''' Appends value to the end of existing key list 
        '''

        if not key in self.p:
            return 

        ## compatibility with version 1 (remove)
        if not self.extended:
            self.p[key].append(value)
            return
        ## ---------------------------------------

        if "value" in self.p[key]:
            self.p[key]['value'].append(value)

    def getModelSet (self):
        ''' Returns a Boolean indicating if the model uses external input
            sources and a list with these sources 
        '''
        ext_input = False
        model_set = None

        if self.getVal('ext_input'):
            model_set = self.getVal('model_set')
            if model_set is not None:
                if len(model_set) > 1:
                    ext_input = True

        return ext_input, model_set

    def dumpJSON (self):
        return json.dumps(self.p)

