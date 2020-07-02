"""
Gets user settings (from settings.py module) and create the final configuration values.
All the rest of the code reads configuration values from this module.
"""
import os
from multiprocessing import cpu_count
from pathlib import Path

import settings


#
# PhenoPLIER, general file structure
#
ROOT_DIR = os.environ.get("PHENOPLIER_ROOT_DIR", settings.ROOT_DIR)

# DATA_DIR stores input data
DATA_DIR = Path(ROOT_DIR, "data").resolve()

# RESULTS_DIR stores newly generated data
RESULTS_DIR = Path(ROOT_DIR, "results").resolve()

#
# General
#
GENERAL = {}
GENERAL["BIOMART_GENES_INFO_FILE"] = Path(
    DATA_DIR, "biomart_genes_hg38.csv.gz"
).resolve()

# CPU usage
options = [settings.N_JOBS, int(cpu_count() / 2)]
GENERAL["N_JOBS"] = next(opt for opt in options if opt is not None)

options = [settings.N_JOBS_HIGH, cpu_count()]
GENERAL["N_JOBS_HIGH"] = next(opt for opt in options if opt is not None)

#
# Results
#
RESULTS = {}
RESULTS["BASE_DIR"] = RESULTS_DIR
RESULTS["PROJECTIONS"] = Path(RESULTS["BASE_DIR"], "projections").resolve()

#
# Manuscript
#
MANUSCRIPT = {}
MANUSCRIPT["BASE_DIR"] = os.environ.get(
    "PHENOPLIER_MANUSCRIPT_DIR", settings.MANUSCRIPT_DIR
)
if MANUSCRIPT["BASE_DIR"] is not None:
    MANUSCRIPT["FIGURES_DIR"] = Path(
        MANUSCRIPT["BASE_DIR"], "content", "images"
    ).resolve()

#
# recount2
#
RECOUNT2 = {}
RECOUNT2["BASE_DIR"] = Path(DATA_DIR, "recount2").resolve()
RECOUNT2["PREPROCESSED_GENE_EXPRESSION_FILE"] = Path(
    RECOUNT2["BASE_DIR"], "recount_data_prep_PLIER.RDS"
).resolve()

#
# UK Biobank paths
#
UK_BIOBANK = {}
UK_BIOBANK["BASE_DIR"] = Path(DATA_DIR, "uk_biobank").resolve()
UK_BIOBANK["CODINGS_DIR"] = Path(UK_BIOBANK["BASE_DIR"], "codings").resolve()
UK_BIOBANK["CODING_3_FILE"] = Path(UK_BIOBANK["CODINGS_DIR"], "coding3.tsv").resolve()
UK_BIOBANK["CODING_6_FILE"] = Path(UK_BIOBANK["CODINGS_DIR"], "coding6.tsv").resolve()

#
# MultiPLIER
#
MULTIPLIER = {}
MULTIPLIER["BASE_DIR"] = Path(DATA_DIR, "multiplier").resolve()
MULTIPLIER["RECOUNT2_MODEL_FILE"] = Path(
    MULTIPLIER["BASE_DIR"], "recount_PLIER_model.RDS"
).resolve()

#
# PhenomeXcan
#
PHENOMEXCAN = {}
PHENOMEXCAN["BASE_DIR"] = Path(DATA_DIR, "phenomexcan").resolve()
# PHENOMEXCAN.DATA_DIR = Path(PHENOMEXCAN.BASE_DIR, "data").resolve()
PHENOMEXCAN["GENE_ASSOC_DIR"] = Path(PHENOMEXCAN["BASE_DIR"], "gene_assoc").resolve()

# Genes metadata and mappings
PHENOMEXCAN["GENES_METADATA_DIR"] = Path(
    PHENOMEXCAN["BASE_DIR"], "genes_metadata"
).resolve()
PHENOMEXCAN["GENE_MAP_ID_TO_NAME"] = Path(
    PHENOMEXCAN["GENES_METADATA_DIR"], "genes_mapping_id_to_name.pkl",
).resolve()
PHENOMEXCAN["GENE_MAP_NAME_TO_ID"] = Path(
    PHENOMEXCAN["GENES_METADATA_DIR"], "genes_mapping_name_to_id.pkl",
).resolve()

# GWAS info
PHENOMEXCAN["RAPID_GWAS_PHENO_INFO_FILE"] = Path(
    PHENOMEXCAN["BASE_DIR"], "phenotypes.both_sexes.tsv.gz"
).resolve()
PHENOMEXCAN["RAPID_GWAS_DATA_DICT_FILE"] = Path(
    PHENOMEXCAN["BASE_DIR"], "UKB_Data_Dictionary_Showcase.tsv"
).resolve()
PHENOMEXCAN["GTEX_GWAS_PHENO_INFO_FILE"] = Path(
    PHENOMEXCAN["BASE_DIR"], "gtex_gwas_phenotypes_metadata.tsv"
).resolve()