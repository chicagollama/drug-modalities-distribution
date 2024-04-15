#!/usr/bin/env python3

import os
import pandas as pd
import plotly.express as px

from subcellular_parse import SubcellularUniprot
import config as config
from plotter import Plotter
from common import Log
from merge import get_merged


class DMD:
    def __init__(self):
        self.job = "dmd"
        self.work_path = config.results_dir
        self.do_merge = get_merged()
        self.merge_csv = os.path.join(self.work_path, "merged.csv")
        self.df = pd.read_csv(self.merge_csv)
        self.log = Log(job=self.job)

        # Get subcellular notations
        self.sc = SubcellularUniprot()

        # Get plotter
        self.plotter = Plotter(job="dmd")

    def df_info(self):
        info = f'\n' \
               f'{"#" * 100}\n\n' \
               f'Plotting merged DMD data!\n\n' \
               f'{"#" * 100}\n\n' \
               f'Got dataframe of {len(self.df.index)} rows\n\n' \
               f'Resulting htmls in {config.html_dir}\n\n'

        self.log.get_log(info=info)

        return info

    def common_locations(self):
        # Group: targetLocationName | drugType
        locs_drugcount = self.df.groupby('targetLocationName').drugType.value_counts().sort_index().reset_index()
        locs_drugcount.columns = ['targetLocationName', 'drugType', 'drugCount']

        # All locations | all drug modalities
        fig1 = self.plotter.plot_scatter(idf=locs_drugcount,
                                         title="Fig. 1. All locations | all drug modalities")

        return fig1

    def clusters(self):
        # Group: targetLocationCluster | drugType
        clusters_drugcount = self.df.groupby('targetLocationCluster').drugType.value_counts().sort_index().reset_index()
        clusters_drugcount.columns = ['targetLocationCluster', 'drugType', 'drugCount']
        fig4 = self.plotter.plot_scatter(idf=clusters_drugcount,
                                         title="Fig. 4. Clusters | drug modalities")

        # Clusters counted for all locations without reduction
        # Group: targetLocationCluster | drugId
        all_clusters = self.df.groupby('targetLocationCluster', as_index=False).drugId.count()
        fig3 = self.plotter.plot_pie_chart(idf=all_clusters,
                                           color_map="cluster",
                                           title="Fig. 3. Clusters counted for all locations without reduction")

        # Group: targetLocationCluster | targetLocationName
        double_drugcount = self.df.groupby(['targetLocationCluster', 'targetLocationName']).drugType.value_counts().reset_index()

        fig2 = self.plotter.plot_sunbirst(idf=double_drugcount, path=['targetLocationCluster', 'targetLocationName'],
                                          title='Fig. 2. Clusters | locations | all drugs')
        fig5 = self.plotter.plot_sunbirst(idf=double_drugcount, path=['targetLocationCluster', 'drugType'],
                                          title='Fig. 5. Clusters | drug modality | all drugs')

        return fig2, fig3, fig4, fig5

    def mlp(self):
        # Group by locations
        mlp_all_df = self.df.groupby('drugId', as_index=False).targetLocationName.count()
        mlp_all_df.columns = ['drugId', 'locationCount']
        drug_with_max_locs = mlp_all_df.iloc[mlp_all_df['locationCount'].idxmax()]
        print("\nMax locations:\n", drug_with_max_locs)

        # Group by locations count
        double_mlp = mlp_all_df.groupby('locationCount', as_index=False).drugId.count()

        # Multiple locations per drug
        fig6 = self.plotter.plot_hist(idf=double_mlp, nbins=300,
                                      title="Fig. 6. MLP | Number of location per target | All drugs")

        # Get MLP as column

        # Label all for location count & MLP flag
        # Add location count and get MLP status for all drugs
        df_with_mlp = pd.merge(self.df, mlp_all_df, on="drugId")
        df_with_mlp["multipleLocations"] = df_with_mlp.apply(lambda row: "ML" if row.locationCount > 1 else "SL", axis=1)

        # Group by MLP | targetLocationName
        loc_mlp = df_with_mlp.groupby('targetLocationName').multipleLocations.value_counts().reset_index()

        # Distribution of ML on targetLocations !!!!!!!
        fig7 = self.plotter.plot_sunbirst(idf=loc_mlp, path=['multipleLocations', 'targetLocationName'],
                                          title='Fig. 7. MLP | Locations distribution | All drugs')

        return fig6, fig7

    def reduce_locations(self):
        """
        REDUCE LOCATIONS DIVERSITY
        TO CLUSTERS DISTRIBUTION
        MAYBE, IT'LL DELETE MOST MLPS
        SPOILER: IT DID :)
        Result: Reduced clusters are more balanced
        """
        # Get clusters count
        # Group by drugId | targetLocationCluster
        clust_count = self.df.groupby('drugId').targetLocationCluster.value_counts().reset_index()

        # Group by drugId | clusterCount
        clust_double_count = clust_count.groupby('drugId').targetLocationCluster.count().reset_index()

        # Circle for Clusters | All drugs
        clusters_all_relative = clust_count.groupby('targetLocationCluster').drugId.count().reset_index()
        fig8 = self.plotter.plot_pie_chart(idf=clusters_all_relative,
                                           color_map="cluster",
                                           title="Fig. 8. Clusters distribution | All drugs | Locations reduced to clusters")

        # >>> Compare to non-reduced:
        # >>> Clusters counted for all locations without reduction
        # >>> Group: targetLocationCluster | drugId
        all_clusters = self.df.groupby('targetLocationCluster', as_index=False).drugId.count()
        fig81 = self.plotter.plot_pie_chart(idf=all_clusters, color_map="cluster",
                                            title="(Fig. 3.) Clusters counted for all locations without reduction")

        return fig8, fig81

    def cluster_registry(self):
        """
        :return: dict
        common: {drugId: [(<cluster>, <cluster count>), ], }
        example: {'CHEMBL4594472': [('Cytoplasm', 6), ('Nucleus', 4), ('Surface', 3), ('Secreted', 2)],}
        """
        # Group by drugId | targetLocationCluster
        clust_count = self.df.groupby('drugId').targetLocationCluster.value_counts().reset_index()
        clust_dict = clust_count.groupby('drugId')[['targetLocationCluster', 'count']].apply(lambda g: list(map(tuple, g.values.tolist()))).to_dict()

        return clust_dict

    def average_cluster(self):
        # Add average cluster to df as column
        # Get registry first, not to slow script
        idict = self.cluster_registry()
        self.df["singleClust"] = self.df.apply(lambda row: self.sc.main_cluster(iclust_dict=dict(idict[row.drugId])), axis=1)

        # Group by singleCluster | drugType
        aav_clust = self.df.groupby(['drugId', 'singleClust']).drugType.value_counts().reset_index()
        av_clust = aav_clust.drop(['count'], axis=1)
        clust_modality = av_clust.groupby('singleClust').drugType.value_counts().reset_index()

        # Average cluster | drug modality
        fig9 = self.plotter.plot_sunbirst(idf=clust_modality, path=['singleClust', 'drugType'],
                                          title='Fig. 9. Average cluster | drug modality | all drugs')

        return fig9

    def average_cluster_vs_modality(self):
        """
        AB | SM | PR -> Cluster || single cluster mode
        Discover the most crowded modalities: Small molecule & Antibody & Protein
        :return: list of fig objects
        """
        # TODO: make av_clust reusable
        # Group by singleCluster | drugType
        aav_clust = self.df.groupby(['drugId', 'singleClust']).drugType.value_counts().reset_index()
        av_clust = aav_clust.drop(['count'], axis=1)

        # TODO: Plot as subplots
        figs = []
        for itype in ('Small molecule', 'Antibody', 'Protein'):
            modality_avclust = av_clust[av_clust.drugType == itype].reset_index()
            plot_modality_avclust = modality_avclust.groupby('singleClust').drugId.count().reset_index()
            fig10 = self.plotter.plot_pie_chart(idf=plot_modality_avclust,
                                                color_map="cluster",
                                                title=f'Fig. 10.{len(figs) + 1}. Average cluster | {itype}')
            figs.append(fig10)

        return figs

    def average_cluster_vs_cluster(self):
        """
        Clusters -> drug modality || single cluster mode
        :return: list of fig objects
        """
        # TODO: make av_clust reusable
        # Group by singleCluster | drugType
        aav_clust = self.df.groupby(['drugId', 'singleClust']).drugType.value_counts().reset_index()
        av_clust = aav_clust.drop(['count'], axis=1)

        # TODO: Plot as subplots
        figs = []
        for iclust in self.sc.global_locs().keys():
            cluster_avclust = av_clust[av_clust.singleClust == iclust].reset_index()
            plot_cluster_avclust = cluster_avclust.groupby('drugType').drugId.count().reset_index()
            fig11 = self.plotter.plot_pie_chart(idf=plot_cluster_avclust,
                                                color_map="modality",
                                                title=f'Fig. 11.{len(figs) + 1} Average cluster | {iclust}')
            figs.append(fig11)
        return figs

    def adc_check(self):
        """
        Seems like there some anomaly in Antibody's locations/clusters
        Though they can't get into the cell
        How can they be so much linked to Cytoplasm proteins?
        Spoiler: Well, not so much :(
        :return: str
        """
        info = ["\n\nCHECK FOR ADC\n", ]
        # Take AB with single cluster Cytoplasm | Nucleus
        # It's not strict check, but a hint: ADCs usually have name like 'LIFASTUZUMAB VEDOTIN'

        for iclust in ('Nucleus', 'Cytoplasm'):
            adc_check = self.df[(self.df.drugType == 'Antibody') & (self.df.singleClust == iclust)].reset_index()
            names = list(set(list(adc_check.drugName)))
            adcs = [i for i in names if ' ' in i]
            info.append(f'{len(adcs)} ADC from {len(names)} for {iclust}\n')

        str_info = '\n'.join(info)
        self.log.get_log(info=str_info)

        return str_info


if __name__ == "__main__":
    dmd = DMD()
    dmd.df_info()
    dmd.common_locations()
    dmd.clusters()
    dmd.mlp()
    dmd.reduce_locations()
    dmd.average_cluster()
    dmd.average_cluster_vs_modality()
    dmd.average_cluster_vs_cluster()
    dmd.adc_check()
