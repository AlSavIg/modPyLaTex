#!/usr/bin/python

# complex_report.py

import random
from pylatex import Document, LongTable, Math, MeasurementsRepr, Label, Marker, Ref, THREE_DIGITS_AFTER_COMMA, NoEscape
from pylatex.utils import bold
from sympy import *
from sympy.abc import W, R
import pandas as pd


def generate_unique():
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    doc = Document(geometry_options=geometry_options, language='russian')

    t_head_names = ["chanel", "measurement"]
    table_1 = pd.read_csv("../data/table_1.csv", sep=";", names=t_head_names)

    # Add statement table
    with doc.create(LongTable("| l | c |")) as longtable_1:
        longtable_1.add_hline()
        for index, row in table_1.iterrows():
            if index == 0:
                longtable_1.add_row([row.chanel, row.measurement],
                                    mapper=bold,
                                    color="lightgray")
            else:
                # print(row.chanel)
                longtable_1.add_row([NoEscape(row.chanel), row.measurement])
            longtable_1.add_hline()

        label = Label(Marker("table:1"))
        longtable_1.add_caption("Моя подпись")
        longtable_1.append(label)
 
    with doc.create(LongTable("| l | c | r |",
                              row_height=1.5)) as data_table:
        data_table.add_hline()
        data_table.add_row(["Measure", "Abs_err", "Full text"],
                           mapper=bold,
                           color="lightgray")
        # data_table.add_empty_row()

        data_table.add_hline()

        for i in range(50):
            measures_config = {
                "show_rel_err": True,
                "no_exp": True,
                "only_measured_val": True,
                "only_err": False,
                "change_exp": 0,
                "factor_out_err_exp": False,
            }

            mea_repr = MeasurementsRepr((random.random() - 0.5) * 10 ** -3, (random.random()) * 10 ** -4)
            mea_repr.set_config(**measures_config)
            measure = Math(data=[mea_repr.latex()], escape=False, inline=True)

            measures_config.update(only_measured_val=False,
                                   only_err=True)
            mea_repr.set_config(**measures_config)
            abs_err = Math(data=[mea_repr.latex()], escape=False, inline=True)

            measures_config.update(only_measured_val=False,
                                   only_err=False,
                                   factor_out_err_exp=True,
                                   no_exp=False)
            mea_repr.set_config(**measures_config)
            full_line = Math(data=[mea_repr.latex()], escape=False, inline=True)

            row = [measure, abs_err, full_line]
            data_table.add_row(row)
            data_table.add_hline()

        label = Label(Marker("table:2"))
        data_table.add_caption("Моя подпись")
        data_table.append(label)

    # doc.append(NewPage())
    f = sqrt(W ** 2 + R ** 2)
    delta_R = IndexedBase(r"\Delta")
    delta_W = IndexedBase(r"\Delta")

    delta_f = sqrt((Derivative(f, W) * delta_R[R]) ** 2 + (Derivative(f, R) * delta_W[W]) ** 2)
    sub = {
        R: 3,
        W: 2,
        delta_R[R]: 0.1,
        delta_W[W]: 0.3
    }
    derivatives = delta_f.doit()
    evaluated = derivatives.evalf(subs=sub)

    mea_repr = MeasurementsRepr(float(evaluated), THREE_DIGITS_AFTER_COMMA)
    measures_config.update(only_measured_val=True, only_err=False, factor_out_err_exp=True, no_exp=False)
    mea_repr.set_config(**measures_config)

    doc.append(Math(data=[
        f"{latex(delta_f)} = {latex(derivatives)} = {mea_repr.latex()}",
    ],
        escape=False)
    )
    doc.append("Этот текст ссылается на Таблицу ")
    doc.append(Ref(Marker("table:2")))
    doc.generate_tex("../pages/complex_report")


if __name__ == '__main__':
    generate_unique()
