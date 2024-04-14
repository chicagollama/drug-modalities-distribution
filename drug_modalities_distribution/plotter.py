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
        self.template=config.template

    def html_file(self, title):
        return os.path.join(self.dir, f'{self.job}_{title.replace(" ", "_").replace("|", "_").replace(":", "_")}.html')

    def plot_scatter(self, idf, title):
        columns = list(idf.columns)
        fig = px.scatter(
            idf,
            title=title,
            x=columns[0],
            y=columns[2],
            color=columns[1],
            log_y=True
        )
        fig.update_layout(
            font=self.font,
            template=self.template
        )

        fig.show()
        return fig

    def plot_pie_chart(self, idf, title, no_labels=False):
        columns = list(idf.columns)
        fig = px.pie(
            idf,
            values=columns[1],
            names=columns[0],
            title=title)
        fig.update_layout(
            font=self.font,
            template=self.template
        )
        if no_labels:
            fig.update_traces(textinfo='none')

        fig.show()
        return fig

    def plot_hist(self, idf, title, nbins=None):
        print(title)
        columns = list(idf.columns)
        fig = px.histogram(
            idf,
            title=title,
            x=columns[0],
            y=columns[-1],
            nbins=nbins
        )
        fig.update_xaxes(categoryorder='total descending')
        fig.update_layout(
            font=self.font,
            template=self.template
        )

        # fig.write_html("test.html")
        fig.write_html(self.html_file(title=title))
        fig.show()

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

        fig.show()
