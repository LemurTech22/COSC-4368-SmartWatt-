import pandera.pandas as pa
from pandera import Column, Check
#add checks for dates, Usage KWH and Estimated Actual what is consumption surplus?
energy_schema = pa.DataFrameSchema(
    columns={
        "ESIID": Column(str,nullable=False,
                        checks=Check.isin(['Alfa','Bravo','Charlie',
                                          'Delta','Echo','Foxtrot',
                                          'Golf','Kilo','Lima'])),
        "USAGE_DATE": Column(str, nullable=False),
        "REVISION_DATE": Column(str, nullable=False),
        "USAGE_START_TIME": Column(str, nullable=False),
        "USAGE_END_TIME": Column(str, nullable=False),
        "USAGE_KWH": Column(float, nullable=False),
        "ESTIMATED_ACTUAL": Column(str, nullable=False,
                                   checks=Check.isin(['A','E'])),
        "CONSUMPTION_SURPLUSGENERATION": Column(str, nullable=False,
                                                checks=Check.isin(["Consumption"])),
    },
        checks=[
            Check(lambda df: len(df) >1000, error="Row Count Too Low")
        ]
)