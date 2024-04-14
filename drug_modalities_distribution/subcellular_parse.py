#!/usr/bin/env python3

import os
from collections import defaultdict
import config as config


class SubcellularUniprot:
    def __init__(self, data_file=config.sc_file):
        self.data_file = data_file
        # self.data_file = config.sc_file

    def data_from_subcellular_db(self):
        subcellular_dict = {}
        with open(self.data_file, 'r') as indata:
            data = indata.readlines()[43:]
            data_str = "".join([el.replace('//\n', 'SPLITTER') for el in data])
            blocks = data_str.split("SPLITTER")[:-1]
            for iblock in blocks:
                if iblock.startswith('ID'):
                    first = iblock.split('\n')[0]
                    name = first.split('ID   ')[-1].split('.')[0].strip()
                    subcellular_dict[name] = {}
                    for row in iblock.split('\n')[1:]:
                        if row.strip() != '':
                            ikey, ivalue = row[:2], row[2:].strip()
                            if ikey not in subcellular_dict[name]:
                                subcellular_dict[name][ikey] = ivalue
                            else:
                                prev = subcellular_dict[name][ikey]
                                subcellular_dict[name][ikey] = prev + ivalue
        return subcellular_dict

    def code_name_dict(self):
        """
        Get short dict {code: name} from uniprot sucellular dict
        """
        full = self.data_from_subcellular_db()
        return {full[name]['AC']: name for name in full.keys()}

    def translate(self, item):
        """
        Translate name to code or backwards
        """
        code_name = self.code_name_dict()
        name_code = {v: k for k, v in self.code_name_dict().items()}
        out = None
        if item in code_name.keys():
            out = code_name[item]
        elif item in code_name.values():
            out = name_code[item]
        else:
            # print(f'SubcellularUnirpot: "{item}" is neither name or code in Uniprot SL!')
            pass
        return out

    def translate_list(self, item_list):
        """
        Translate name to code or backwards for the list of items
        """
        translated = [self.translate(item) for item in item_list]
        return translated

    @staticmethod
    def global_locs():
        clusters = {
            "Secreted": ['Secreted', ],
            "Surface":
                ['Apical cell membrane', 'Basal cell membrane', 'Basolateral cell membrane', 'Cell membrane',
                 'Cell surface',
                 'Endosome membrane', 'Lateral cell membrane', 'Postsynaptic cell membrane',
                 'Presynaptic cell membrane'],
            "Cytoplasm":
                ['Cell junction', 'Cell projection', 'Centriolar satellite', 'Cleavage furrow',
                 'Cytolytic granule membrane',
                 'Cytoplasm', 'Cytoplasmic granule', 'Cytoplasmic ribonucleoprotein granule', 'Cytoplasmic vesicle',
                 'Cytoplasmic vesicle lumen', 'Cytoplasmic vesicle membrane', 'Cytoskeleton', 'Cytosol',
                 'Dynein axonemal particle',
                 'Early endosome', 'Early endosome membrane', 'Endomembrane system', 'Endoplasmic reticulum',
                 'Endoplasmic reticulum lumen', 'Endoplasmic reticulum membrane', 'Endosome', 'Endosome lumen',
                 'Extracellular vesicle', 'Focal adhesion', 'Golgi apparatus', 'Golgi apparatus membrane',
                 'Golgi outpost',
                 'Inflammasome', 'Late endosome', 'Late endosome membrane', 'Lipid droplet', 'Lysosome',
                 'Lysosome lumen',
                 'Lysosome membrane', 'Melanosome', 'Melanosome membrane', 'Membrane', 'Membrane raft', 'Microsome',
                 'Microsome membrane', 'Midbody', 'Midbody ring', 'Mitochondrion', 'Mitochondrion inner membrane',
                 'Mitochondrion intermembrane space', 'Mitochondrion matrix', 'Mitochondrion membrane',
                 'Mitochondrion outer membrane', 'Perikaryon', 'Peroxisome', 'Peroxisome matrix', 'Peroxisome membrane',
                 'Photoreceptor inner segment', 'Postsynapse', 'Postsynaptic density', 'Postsynaptic density membrane',
                 'Presynapse', 'Recycling endosome', 'Recycling endosome membrane', 'Rough endoplasmic reticulum',
                 'Sarcoplasmic reticulum membrane', 'Synapse', 'Vesicle', 'Virion'],
            "Nucleus":
                ['Nuclear body', 'Nucleolus', 'Nucleolus fibrillar center', 'Nucleoplasm', 'Nucleus',
                 'Nucleus envelope',
                 'Nucleus inner membrane', 'Nucleus intermembrane space', 'Nucleus lamina', 'Nucleus matrix',
                 'Nucleus membrane',
                 'Nucleus outer membrane', 'Nucleus speckle', 'Centrosome', 'Chromosome', 'Spindle']
        }
        return clusters

    def get_cluster(self, sl_code: str) -> [str | None]:
        """Check if target is surface by Uniprot SL code"""
        clusters = self.global_locs()

        global_loc = "Unknown"
        for cluster in clusters:
            if self.translate(sl_code) in clusters[cluster]:
                global_loc = cluster
        return global_loc

    @staticmethod
    def main_cluster(iclust_dict):
        """
        Tool for choosing single average cluster for drugs with several clusters
        :param iclust_dict: {'CHEMBL4594472': [('Cytoplasm', 6), ('Nucleus', 4), ('Surface', 3), ('Secreted', 2)],}
        :return: str | single cluster name
        """
        priority = ['Surface', 'Secreted', 'Nucleus', 'Cytoplasm']
        priority.reverse()

        b = defaultdict(list)
        for key, val in iclust_dict.items():
            b[val].append(key)
        max_clust = b[max(b)]

        if len(max_clust) > 1:
            # TODO: set better choice logic
            single_clust = max(max_clust, key=lambda m: priority.index(m))
        else:
            single_clust = max_clust[0]
        return single_clust


# if __name__ == "__main__":
    # entity = input()
    # sc = SubcellularUniprot()
    # print(sc.translate(entity))
