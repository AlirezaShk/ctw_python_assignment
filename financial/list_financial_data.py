from model import FinancialData
from typing import Optional, List, Tuple
from datetime import datetime
from lib.logging import Loggable
from math import ceil
from lib.exceptions import PageOutofBoundsError


@Loggable("list_financial_data")
def main(
    limit: int,
    page: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    symbol: Optional[str] = None
) -> Tuple[int, List[FinancialData]]:
    """Returns a paginated list of financial data records saved in DB.

    Args:
        limit (int): required
        page (int): required
        start_date (Optional[datetime], optional): Defaults to None.
        end_date (Optional[datetime], optional): Defaults to None.
        symbol (Optional[str], optional): Defaults to None. If None, all symbols will be targeted.

    Raises:
        PageOutofBoundsError: If the `page` argument is more than the max page, this will be raised.

    Returns:
        Tuple[int, List[FinancialData]]: A tuple containing: {
            total: Total number of records in the Database, matching the query,
            data: Array of FinancialData records
        }
    """
    total = 0
    paginated = {}
    base_query = FinancialData.query
    if base_query.count() == 0:
        return 0, []
    if symbol:
        base_query = base_query.filter_by(symbol=symbol)
    if start_date:
        base_query = base_query.filter(FinancialData.date >= start_date)
    if end_date:
        base_query = base_query.filter(FinancialData.date <= end_date)
    total = base_query.count()
    if total == 0:
        return total, []
    max_ = ceil(float(total) / limit)
    if page > max_:
        raise PageOutofBoundsError(asked=page, max_=max_)
    paginated = base_query.paginate(page=page, per_page=limit)
    return total, paginated.items
