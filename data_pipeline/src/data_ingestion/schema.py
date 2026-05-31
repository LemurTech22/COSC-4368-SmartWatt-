import pandera.pandas as pa
from pandera import Column, Check
#add checks for dates, Usage KWH and Estimated Actual what is consumption surplus? same thing for weather modify extractor to gain more insight
energy_schema = pa.DataFrameSchema(
    columns={
        "ESIID": Column(str,nullable=False,
                        checks=Check.isin(['Alfa', 'Bravo', 'Charlie',
                                           'Delta', 'Echo', 'Foxtrot',
                                            'Golf','Hotel', 'India', 
                                            'Juliett', 'Kilo', 'Lima'])),
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

weather_schema = pa.DataFrameSchema(
    columns={
        'temp': Column(float, nullable=False),
        'dwpt': Column(float, nullable=False),
        'rhum': Column(float, nullable=False),
        'prcp': Column(float, nullable=True),
        'snow': Column(float, nullable=True),
        'wdir': Column(float, nullable=False),
        'wspd': Column(float, nullable=False),
        'wpgt': Column(float, nullable=True),
        'pres': Column(float, nullable=False),
        'tsun': Column(float, nullable=True),
        'coco': Column(float, nullable=True),
    },
        checks=[Check(
            lambda df: len(df) > 0, error= "Error Count To low | No data pulled "
            )
        ]
        
)