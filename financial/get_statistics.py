from lib.logging import Loggable
from datetime import datetime
from typing import Dict
from model import FinancialData
from conf.settings import MAX_BULK_OPERATIONS
import pandas as pd
from app import cache


@Loggable("get_statistics")
@cache.memoize(50)
def main(
    start_date: datetime,
    end_date: datetime,
    symbol: str
) -> Dict[str, float]:
    """Returns average daily statistics data of the target symbol

    Args:
        start_date (datetime): required
        end_date (datetime): required
        symbol (str): required

    Returns:
        Dict[str, float]: A Dictionary containing: {
                "start_date": fields.Date
                "end_date": fields.Date
                "symbol": fields.String
                "average_daily_open_price": fields.Float
                "average_daily_close_price": fields.Float
                "average_daily_volume": fields.Float
            }
    """
    cols = ['symbol', 'open_price', 'close_price', 'volume']
    query = FinancialData.query.filter_by(symbol=symbol).filter(FinancialData.date.between(start_date, end_date))
    if query.count() == 0:
        return {}
    # TODO: Optimize the Database Call and Pandas Dataframe Creation/Concatenation
    # The opeartor `.with_entities(*[getattr(FinancialData, col) for col in cols])` could
    # be used to specify which columns to retrieve from DB, but in the `pd.concat(...)` part
    # later on, this will cause an issue, as the results will not have a `.to_dict()` attribute
    # and will be a list of tuples instead.
    res = query.paginate(page=1, per_page=MAX_BULK_OPERATIONS)
    avg_df = calc_mean(res, columns=cols)
    avg_df.rename(columns={col: f"average_daily_{col}" for col in cols[1:]}, inplace=True)
    return dict(avg_df.iloc[0])


def calc_mean(paginated_items, columns) -> pd.DataFrame:
    df = pd.DataFrame(columns=columns)
    while paginated_items.items:
        df = pd.concat([df, pd.DataFrame(map(lambda x: x.to_dict(), paginated_items.items), columns=columns)])
        paginated_items = paginated_items.next()
    # End while
    df['volume'] = df['volume'].astype(float)
    # breakpoint()
    return df.groupby('symbol').agg('mean', numeric_only=True)
