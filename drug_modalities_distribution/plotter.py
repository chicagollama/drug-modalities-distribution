#!/usr/bin/env python3

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os
import config as config


class Plotter:
    def __init__(self, job):
        self.dir = config.html_dir
        self.job = job
        self.font = dict(size=20)
        self.template = config.template

        # Set color scheme for drug modalities & target locations clusters
        # To plot same colors for different tasks & compare easily
        self.plotly_colors = px.colors.qualitative.Plotly
        self.modalities = ('Small molecule', 'Antibody', 'Protein', 'Unknown', 'Oligonucleotide', 'Oligosccharide',
                           'Enzyme', 'Gene', 'Cell')
        self.color_map_modality = {self.modalities[_]: self.plotly_colors[_] for _ in range(len(self.modalities))}
        self.cluster_list = ('Surface', 'Cytoplasm', 'Nucleus', 'Secreted')
        self.color_map_cluster = {self.cluster_list[_]: self.plotly_colors[_] for _ in range(len(self.cluster_list))}

    def get_colors(self, option):
        """Choose the color map"""
        map = None
        if option == "cluster":
            map = self.color_map_cluster
        elif option == "modality":
            map = self.color_map_modality
        return map

    def html_file(self, title):
        return os.path.join(self.dir, f'{self.job}_{title.replace(" ", "_").replace("|", "_").replace(":", "_")}.html')

    def plot_scatter(self, idf, title, log_y=True):
        columns = list(idf.columns)
        fig = px.scatter(
            idf,
            title=title,
            x=columns[0],
            y=columns[2],
            color=columns[1],
            log_y=log_y
        )
        fig.update_layout(
            font=self.font,
            template=self.template,
        )
        fig.update_traces(marker_size=20)

        fig.write_html(self.html_file(title=title))
        # fig.show()
        return fig

    def plot_pie_chart(self, idf, title,  color_map=None, no_labels=False):
        columns = list(idf.columns)

        if color_map:
            fig = px.pie(
                idf,
                values=columns[1],
                names=columns[0],
                title=title,
                color=columns[0],
                color_discrete_map=self.get_colors(color_map),
            )

        else:
            fig = px.pie(
                idf,
                values=columns[1],
                names=columns[0],
                title=title,
            )

        fig.update_layout(
            title=title,
            font=self.font,
            template=self.template,
            uniformtext_minsize=20,
            uniformtext_mode='hide'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')

        fig.update_traces(hole=.4)

        if no_labels:
            fig.update_traces(textinfo='none')

        fig.write_html(self.html_file(title=title))
        # fig.show()

        return fig

    def plot_hist(self, idf, title, nbins=None):
        columns = list(idf.columns)
        fig = px.histogram(
            idf,
            title=title,
            x=columns[0],
            y=columns[-1],
            nbins=nbins,
        )
        fig.update_xaxes(categoryorder='total descending')
        fig.update_layout(
            font=self.font,
            template=self.template,
            bargap=0.2,
            xaxis=dict(tickmode='linear')

        )

        fig.write_html(self.html_file(title=title))
        # fig.show()

        return fig

    def plot_sunbirst(self, idf, title, path):
        columns = list(idf.columns)
        fig = px.sunburst(
            idf,
            title=title,
            path=path,
            values=columns[-1]
        )
        fig.update_xaxes(categoryorder='total descending')
        fig.update_layout(
            font=self.font,
            template=self.template
        )

        fig.write_html(self.html_file(title=title))
        # fig.show()

        return fig
