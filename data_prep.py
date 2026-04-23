import pandas as pd
from pathlib import Path


def load_and_prepare_data():
    # Load datasets
    slum = pd.read_csv("data_raw/WB_WDI_EN_POP_SLUM_UR_ZS.csv")
    urban = pd.read_csv("data_raw/WB_WDI_SP_URB_TOTL.csv")

    # Keep only required columns
    slum = slum[["REF_AREA", "REF_AREA_LABEL", "TIME_PERIOD", "OBS_VALUE"]]
    urban = urban[["REF_AREA", "REF_AREA_LABEL", "TIME_PERIOD", "OBS_VALUE"]]

    # Rename columns
    slum = slum.rename(columns={
        "REF_AREA": "country_code",
        "REF_AREA_LABEL": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "slum_pct"
    })

    urban = urban.rename(columns={
        "REF_AREA": "country_code",
        "REF_AREA_LABEL": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "urban_pop"
    })

    # Convert types
    slum["year"] = pd.to_numeric(slum["year"], errors="coerce")
    urban["year"] = pd.to_numeric(urban["year"], errors="coerce")
    slum["slum_pct"] = pd.to_numeric(slum["slum_pct"], errors="coerce")
    urban["urban_pop"] = pd.to_numeric(urban["urban_pop"], errors="coerce")

    # Merge on shared keys
    df = pd.merge(
        slum,
        urban,
        on=["country_code", "country", "year"],
        how="inner"
    )

    # Keep overlapping analysis period
    df = df[(df["year"] >= 2000) & (df["year"] <= 2022)]

    # Remove missing values
    df = df.dropna(subset=["slum_pct", "urban_pop"])

    # Remove aggregate / regional rows using codes
    aggregate_codes = {
        "AFE", "AFW", "ARB", "CEB", "CSS", "EAP", "EAR", "EAS", "ECA", "ECS",
        "EMU", "EUU", "FCS", "HIC", "HPC", "IBD", "IBT", "IDA", "IDB", "IDX",
        "LAC", "LCN", "LDC", "LIC", "LMC", "LMY", "LTE", "MEA", "MIC", "MNA",
        "NAC", "OED", "OSS", "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST",
        "TEA", "TEC", "TLA", "TMN", "TSA", "TSS", "UMC", "WLD"
    }

    df = df[~df["country_code"].isin(aggregate_codes)]

    # Keep only sensible values
    df = df[(df["slum_pct"] >= 0) & (df["slum_pct"] <= 100)]
    df = df[df["urban_pop"] > 0]

    # Core derived metric
    df["slum_population"] = (df["slum_pct"] / 100) * df["urban_pop"]

    # Sort
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    # Create summary metrics using first and last available year per country
    bounds = df.groupby(["country", "country_code"]).agg(
        first_year=("year", "min"),
        last_year=("year", "max")
    ).reset_index()

    start_df = df.merge(
        bounds,
        left_on=["country", "country_code", "year"],
        right_on=["country", "country_code", "first_year"],
        how="inner"
    )

    end_df = df.merge(
        bounds,
        left_on=["country", "country_code", "year"],
        right_on=["country", "country_code", "last_year"],
        how="inner"
    )

    summary = start_df[[
        "country", "country_code", "year", "slum_pct", "urban_pop", "slum_population"
    ]].merge(
        end_df[[
            "country", "country_code", "year", "slum_pct", "urban_pop", "slum_population"
        ]],
        on=["country", "country_code"],
        suffixes=("_start", "_end")
    )

    summary = summary.rename(columns={
        "year_start": "start_year",
        "year_end": "end_year"
    })

    summary["slum_change_total"] = summary["slum_pct_end"] - summary["slum_pct_start"]
    summary["urban_growth_total"] = (
        (summary["urban_pop_end"] - summary["urban_pop_start"]) / summary["urban_pop_start"]
    ) * 100
    summary["slum_population_change_total"] = (
        summary["slum_population_end"] - summary["slum_population_start"]
    )

    # Merge summary back
    df = df.merge(
        summary[[
            "country",
            "country_code",
            "start_year",
            "end_year",
            "slum_change_total",
            "urban_growth_total",
            "slum_population_change_total"
        ]],
        on=["country", "country_code"],
        how="left"
    )

    # Save to correct folder
    output_path = Path("data_processed")
    output_path.mkdir(exist_ok=True)
    df.to_csv(output_path / "final_dataset.csv", index=False)

    return df


if __name__ == "__main__":
    df = load_and_prepare_data()
    print(df.head())
    print(df.shape)