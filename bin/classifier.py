#!/usr/bin/env python2
###############################################################################
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

__author__ = "Ben Woodcroft"
__copyright__ = "Copyright 2017"
__credits__ = ["Ben Woodcroft"]
__license__ = "GPL3+"
__maintainer__ = "Ben Woodcroft"
__email__ = "b.woodcroft near uq.edu.au"
__status__ = "Development"

import os, re
import logging
import pickle

from module_description_parser import ModuleDescription

class Classify:
    
    PICKLE      = 'pickle'

    DATA_PATH   = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
    VERSION     = open(os.path.join(DATA_PATH, 'VERSION')).readline().strip()
    M2DEF       = os.path.join(DATA_PATH, 'module_to_definition')
    M           = os.path.join(DATA_PATH, 'module_descriptions')
    KO_OUTPUT   = "KO_interpretations.tsv"
    
    def __init__(self):

        self.ko_re = re.compile('^K\d+$')
        
        self.signature_modules = set(['M00611', 'M00612', 'M00613', 'M00614',
         'M00617', 'M00618', 'M00615', 'M00616', 'M00363', 'M00542', 'M00574',
         'M00575', 'M00564', 'M00660', 'M00664', 'M00625', 'M00627', 'M00745',
         'M00651', 'M00652', 'M00704', 'M00725', 'M00726', 'M00730', 'M00744',
         'M00718', 'M00639', 'M00641', 'M00642', 'M00643', 'M00769', 'M00649',
         'M00696', 'M00697', 'M00698', 'M00700', 'M00702', 'M00714', 'M00705',
         'M00746'])
        
        logging.info("Loading module definitions")
        self.m2def = pickle.load(open('.'.join([self.M2DEF,
                                                 self.VERSION, self.PICKLE])))
        logging.info("Done!")
        logging.info("Loading module descriptions")
        self.m = pickle.load(open('.'.join([self.M,
                                            self.VERSION, self.PICKLE])))
        logging.info("Done!")
        
    def _update_with_custom_modules(self, custom_modules):
        custom_modules_dict = {line.split('\t')[0]:line.strip().split('\t')[1]
                               for line in open(custom_modules)}
        self.m2def.update(custom_modules_dict)
        
        for key in custom_modules_dict.keys():
            self.m[key] = 'Custom'
    
    def _parse_genome_and_annotation_file_lf(self, genome_and_annotation_file):
        genome_to_annotation_sets = {}
        for line in open(genome_and_annotation_file):
            sline = line.strip().split("\t")
            if len(sline) != 2: raise Exception("Input genomes/annotation file error on %s" % line)
            
            genome, annotation = sline
            
            if self.ko_re.match(annotation):
                if genome not in genome_to_annotation_sets:
                    genome_to_annotation_sets[genome] = set()
                genome_to_annotation_sets[genome].add(annotation)
            else:
                raise Exception("Malformed annotation line: %i" % line)
        return genome_to_annotation_sets
    
    def _parse_genome_and_annotation_file_matrix(self, genome_and_annotation_file):
        genome_and_annotation_file_io = open(genome_and_annotation_file)
        headers=genome_and_annotation_file_io.readline().strip().split('\t')[1:]
        genome_to_annotation_sets = {genome_name:set() for genome_name in headers}

        for line in genome_and_annotation_file_io:
            sline = line.strip().split('\t')
            annotation, entries = sline[0], sline[1:]
            for genome_name, entry in zip(headers, entries):
                if float(entry) > 0:
                    genome_to_annotation_sets[genome_name].add(annotation)
        return genome_to_annotation_sets

    def write(self, lines, output_path):
        
        logging.info('Writing results to file: %s' % output_path)

        with open(output_path, 'w') as output_path_io:
            for line in sorted(lines):
                output_path_io.write(line)      
    def do(self, custom_modules, cutoff, genome_and_annotation_file, 
           genome_and_annotation_matrix, output_directory):
        '''
        
        Parameters
        ----------
        custom_modules                  - string. Path to file containing custom module definitions, 
                                          consistent with KEGG module nomenclature 
                                          (http://www.genome.jp/kegg/module.html)
        cutoff                          - float. Fraction of a module needed in order to be included
                                          in the output.
        genome_and_annotation_file      - string. Path to file containing genome - annotation file. This file 
                                          contains two columns, the first with the genome name, the 
                                          second with a annotation annotation within that genome 
        genome_and_annotation_matrix    - string. Path to file containing genome - annotation matrix
        output                          - string. Path to file to output results to.

        '''
        if custom_modules:
            self._update_with_custom_modules(custom_modules)
        if genome_and_annotation_file:
            genome_to_annotation_sets = self._parse_genome_and_annotation_file_lf(genome_and_annotation_file)
        elif genome_and_annotation_matrix:
            genome_to_annotation_sets = self._parse_genome_and_annotation_file_matrix(genome_and_annotation_matrix)
        logging.info("Read in annotations for %i genomes" % len(genome_to_annotation_sets))
        
        pathway = {}

        output_lines = ['\t'.join(["Genome_name", "Module_id", "Module_name", "Steps_found", 
                             "Steps_needed", "Percent_Steps_found"]) + '\n']
        for name, pathway_string in self.m2def.items():
            if name not in self.signature_modules:   
                path = ModuleDescription(pathway_string)
                pathway[name] = path
                for genome, annotations in genome_to_annotation_sets.items():
                    num_covered = path.num_covered_steps(annotations)
                    num_all = path.num_steps()
                    perc_covered = num_covered / float(num_all)
                    if perc_covered >= cutoff:
                        output_line = "\t".join([genome, name, self.m[name],
                                                  str(num_covered),  # 
                                                  str(num_all),
                                                  str(round(perc_covered * 100, 2))]) 
                        output_lines.append(output_line + '\n') 
        self.write(output_lines, os.path.join(output_directory, self.KO_OUTPUT)) ### ~ TODO: make output flexible
            

