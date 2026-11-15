"""
TERRA-X STAC and GeoParquet Dataset Exporter
Generates open STAC Catalog and GeoJSON/GeoParquet exports of evaluated H3 analog test cells.
"""

import json
from pathlib import Path
from engine.pipeline import TerraXPipeline
from harmonize.h3_grid import H3Grid

OUTPUT_DIR = Path(__file__).resolve().parent

def export_stac_catalog():
    pipeline = TerraXPipeline()
    targets = ["MOON_SOUTH_POLE_SHACKLETON", "MARS_JEZERO_DELTA"]
    functions = ["MOBILITY", "CONSTRUCTION_ISRU", "ASTROBIO"]

    all_features = []

    for target_id in targets:
        for func in functions:
            out = pipeline.run_discovery_pipeline(
                target_id=target_id,
                function_profile=func,
                top_k=20,
            )
            for site in out["ranked_sites"]:
                cell_id = site["cell_id_h3_r6"]
                poly = H3Grid.cell_to_boundary(cell_id)

                feat = {
                    "type": "Feature",
                    "id": f"{site['site_id']}_{target_id}_{func}",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [poly],
                    },
                    "properties": {
                        "site_name": site["site_name"],
                        "country": site["country"],
                        "continent": site["continent"],
                        "cell_id_h3": cell_id,
                        "planetary_target": target_id,
                        "function_profile": func,
                        "afi_score_p50": site["scores"]["afi_p50"],
                        "afi_score_p10": site["scores"]["afi_p10"],
                        "afi_score_p90": site["scores"]["afi_p90"],
                        "M_match": site["scores"]["M_match"],
                        "C_confounder": site["scores"]["C_confounder"],
                        "T_transferable": site["scores"]["T_transferable"],
                        "rank_p50": site["monte_carlo_rank"]["rank_p50"],
                        "p_top10": site["monte_carlo_rank"]["p_top10"],
                        "novelty_score": site["novelty"]["novelty_score"],
                        "stac_version": "1.0.0",
                        "license": site["provenance"]["license_class"],
                        "doi": site["provenance"]["doi"],
                    },
                }
                all_features.append(feat)

    # 1. GeoJSON STAC Collection
    stac_catalog = {
        "type": "FeatureCollection",
        "stac_version": "1.0.0",
        "id": "terrax-global-functional-analogs",
        "description": "TERRA-X NASA Space Apps 2026 Functional Planetary Analog Open STAC Collection",
        "license": "CC-BY-4.0",
        "features": all_features,
    }

    geojson_path = OUTPUT_DIR / "terrax_stac_collection.geojson"
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(stac_catalog, f, indent=2)

    print(f"Exported STAC Collection ({len(all_features)} items) to {geojson_path}")

    # 2. Tabular summary for Pandas / GeoParquet conversion
    try:
        import pandas as pd
        records = [f["properties"] for f in all_features]
        df = pd.DataFrame(records)
        csv_path = OUTPUT_DIR / "terrax_analog_catalog.csv"
        df.to_csv(csv_path, index=False)
        print(f"Exported Tabular Catalog to {csv_path}")
        
        # Parquet export
        parquet_path = OUTPUT_DIR / "terrax_analog_catalog.parquet"
        df.to_parquet(parquet_path, index=False)
        print(f"Exported Parquet Catalog to {parquet_path}")
    except Exception as e:
        print(f"Pandas export note: {e}")

if __name__ == "__main__":
    export_stac_catalog()

