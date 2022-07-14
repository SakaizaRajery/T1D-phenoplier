# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-execution,-papermill,-trusted
#     formats: ipynb,py//py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] tags=[]
# # Description

# %% [markdown] tags=[]
# **FIXME: update**
#
# The idea of this notebook is to explore a simple OLS model (Ordinary Least Squares) to associate an LV (gene weights) with a trait (gene z-scores). Since predicted gene expression is correlated, especially among adjacent genes, a simple OLS model is expected to fail by having high type I errors.

# %% [markdown] tags=[]
# # Modules

# %% tags=[]
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.graphics.gofplots import qqplot_2samples
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

import conf
from data.recount2 import LVAnalysis

# %% [markdown] tags=[]
# # Settings

# %%
N_PHENOTYPES = 1000
N_LVS = 9

# %% tags=[]
INPUT_DIR = conf.RESULTS["GLS_NULL_SIMS"] / "phenoplier" / "gls-1000g_mashr-test-full_corr"
display(INPUT_DIR)

# %%
PVALUE_COLUMN = "pvalue_onesided"
# PVALUE_COLUMN = "pvalue"

# %% [markdown] tags=[]
# # Functions

# %%
def get_prop(pvalues, frac=0.05):
    _pvalue_lt_frac = pvalues[pvalues < frac]
    return _pvalue_lt_frac.shape[0] / pvalues.shape[0]


# %%
def show_prop(data, frac=0.05):
    pvalues = data[PVALUE_COLUMN]
    return get_prop(pvalues, frac=frac)


# %%
assert get_prop(np.array([0.20, 0.50]), 0.05) == 0.0
assert get_prop(np.array([0.20, 0.50, 0.75, 0.10, 0.04]), 0.05) == 0.2

# %%
assert get_prop(pd.Series(np.array([0.20, 0.50])), 0.05) == 0.0
assert get_prop(pd.Series(np.array([0.20, 0.50, 0.75, 0.10, 0.04])), 0.05) == 0.2


# %%
def qqplot_unif(results, other_results=None):
    data = results[PVALUE_COLUMN].to_numpy()
    n = data.shape[0]
    observed_data = -np.log10(data)

    observed_lv = results["lv"].unique()
    assert len(observed_lv) == 1
    observed_lv = observed_lv[0]

    other_lv = ""
    if other_results is not None:
        other_data = other_results[PVALUE_COLUMN].to_numpy()
        expected_data = -np.log10(other_data)

        other_lv = other_results["lv"].unique()
        assert len(other_lv) == 1
        other_lv = other_lv[0]
    else:
        uniform_data = np.array([i / (n + 1) for i in range(1, n + 1)])
        expected_data = -np.log10(uniform_data)

    with sns.plotting_context("paper", font_scale=1.8), mpl.rc_context(
        {"lines.markersize": 3}
    ):
        fig, ax = plt.subplots(figsize=(8, 8))

        fig = qqplot_2samples(expected_data, observed_data, line="45", ax=ax)

        ax.set_xlim(expected_data.min() - 0.05, expected_data.max() + 0.05)

        ax.set_xlabel(f"$-\log_{10}$(expected pvalue) - {other_lv}")
        ax.set_ylabel(f"$-\log_{10}$(observed pvalue) - {observed_lv}")


# %% [markdown]
# # Get files list

# %%
INPUT_FILES = list(INPUT_DIR.glob("*.tsv.gz"))
display(INPUT_FILES[:5])

# %% [markdown]
# # Load data

# %% tags=[]
dfs = [
    pd.read_csv(f, sep="\t").assign(phenotype=f.name.split("-")[0]) for f in INPUT_FILES
]

# %% tags=[]
display(len(dfs))
assert len(dfs) == N_PHENOTYPES

# %% tags=[]
dfs = pd.concat(dfs, axis=0, ignore_index=True)

# %%
display(dfs.shape)
assert dfs.shape[0] == N_PHENOTYPES * N_LVS

# %%
dfs.head()

# %%
_tmp = dfs.groupby("phenotype")["lv"].nunique().unique()
assert _tmp.shape[0] == 1
assert _tmp[0] == N_LVS

# %% [markdown]
# # Mean type I error

# %%
get_prop(dfs[PVALUE_COLUMN], frac=0.05)

# %% [markdown]
# It should be around 0.05. Let's check what happened at individual LVs.

# %% [markdown]
# # Summary of mean type I error per LV

# %%
summary_list = []
for lv, lv_data in dfs.groupby("lv"):
    assert lv_data.shape[0] == N_PHENOTYPES

    summary_list.append(
        {
            "lv": lv,
            "1": get_prop(lv_data[PVALUE_COLUMN], 0.01),
            "5": get_prop(lv_data[PVALUE_COLUMN], 0.05),
            "10": get_prop(lv_data[PVALUE_COLUMN], 0.10),
        }
    )

summary_df = pd.DataFrame(summary_list)
assert summary_df.shape[0] == N_LVS

# %%
summary_df.shape

# %%
summary_df.head()

# %%
summary_df.describe()

# %% [markdown]
# ## LVs with expected type I error

# %%
lvs_expected_error = summary_df[summary_df["5"].between(0.049, 0.051)]
display(lvs_expected_error.shape)
display(lvs_expected_error.sort_values("5").head(20))
display(lvs_expected_error.sort_values("5").tail(20))

# %% [markdown]
# ## LVs with high type I error

# %%
lvs_high_error = summary_df[summary_df["5"] > 0.06]
display(lvs_high_error.shape)
# display(lvs_high_error.sort_values("5").head(20))
display(lvs_high_error.sort_values("5").tail(20))

# %% [markdown]
# Many LVs have a mean type I error greater than expected.
#
# LV45 has the largest mean type I error (0.158). Let's take a look at these LVs with poor mean type I errors.

# %% [markdown]
# # LVs with high mean type I error

# %%
lv_results_high = {}

# %% [markdown]
# ## LV45

# %%
lv_code = "LV45"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# ## LV234

# %%
lv_code = "LV234"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# ## LV847

# %%
lv_code = "LV847"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# ## LV110

# %%
lv_code = "LV110"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# ## LV769

# %%
lv_code = "LV769"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# The QQplot here is not the same as the LVs before. In previous LVs, there are very small pvalues, likely because of the genes from the same region at the top of the LV.
#
# Here p-values are consistently smaller than expected, but there are no very small p-values.

# %% [markdown]
# ## LV800

# %%
lv_code = "LV800"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_high[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# **Note**: looks similar to LV769. This one has smaller minimum p-values.

# %% [markdown]
# ## Notes

# %% [markdown]
# **TODO UPDATE**
#
# There are LVs with high mean type I errors that have different properties:
#
# 1. LVs like LV45-LV110 (the first ones) have:
#     1. Smaller minimum p-values (qqplots deviate late and quickly), with -log(p) around 10 or 20.
#     1. High gene weights (around 6 to 9)...
#     1. Genes from the same band at the top.
#     1. Relatively fewer genes with non-zero (> 0) weights, from ~400 to ~1600.
#     1. Cytobands usually have 1 or 2 genes with non-zero weight, but there are some with many genes.
#         * LV45 has a single band with 13 genes, and all the rest have 8 or less...
#         * ... whereas the rest of these LVs have many bands with many genes (this could explain why LV45 is the worst).
#
# 1. LVs like LV769 have:
#     1. Larger p-values (qqplots deviate early) with -log10(p) around 4
#     1. Lower gene weights (around 2 to 4).
#     1. Genes at the top are not from the same band.
#     1. Larger number of genes with non-zero (> 0) weights, more than 2400.
#     1. Same pattern regarding cybands.
#
# 1. LVs like LV800 are mixed between the other two:
#     1. QQ plots show early deviation but also smaller minimum pvalues.
#     1. Lower gene weights (less than 2)
#     1. Gene weights are a bit more uniform in LV800, with more genes having similar weights around 0.75 or 1.00.
#     1. Genes at the top are from the same band.
#     1. Same pattern regarding cybands.
#
# Besides the ratio of genes with non-zero weights and zero, I didn't find any distinction **among genes with zero weight**.

# %% [markdown]
# # LVs with expected mean type I error

# %%
display(lvs_expected_error.sort_values("5").head(20))

# %% [markdown]
# Here I'm manually selecting from this list, since I want those that are well calibrated across different p-value thresholds.

# %%
lv_results_expected = {}

# %% [markdown]
# ## LV412

# %%
lv_code = "LV412"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_expected[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# **Note**

# %% [markdown]
# ## LV57

# %%
lv_code = "LV57"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_expected[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# **Note**

# %% [markdown]
# Here the distribution do differ, this is more similar to LV769.

# %% [markdown]
# ## LV647

# %%
lv_code = "LV647"

# %%
results = dfs[dfs["lv"] == lv_code]

# %%
results.shape

# %%
results.head()

# %%
# save for future reference
lv_results_expected[lv_code] = results

# %% [markdown]
# ### Mean type I errors at different thresholds

# %%
show_prop(results, 0.01)

# %%
show_prop(results, 0.05)

# %%
show_prop(results, 0.10)

# %%
show_prop(results, 0.15)

# %%
show_prop(results, 0.20)

# %% [markdown]
# ### QQplot

# %%
qqplot_unif(results)

# %% [markdown]
# **Note**

# %% [markdown]
# # Conclusions

# %% [markdown]
# Looks like not-well-calibrated LVs are due to either:
# * Too many top genes from the same band.
# * Or not matched distributions of band sizes between zero and non-zero weighted genes.
# * Too many large bands among the top genes.

# %%
