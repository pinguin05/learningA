import pandas as pd
from sqlalchemy import create_engine

def save_df_to_postgres(df: pd.DataFrame, table_name: str, connection_string: str):
    """
    Сохраняет DataFrame в PostgreSQL с перезаписью существующей таблицы.
    
    Args:
        df: pandas DataFrame для сохранения
        table_name: имя таблицы в PostgreSQL
        connection_string: строка подключения (postgresql://user:pass@host:port/db)
    """
    # Создаем engine для подключения
    engine = create_engine(connection_string)
    
    # Сохраняем с перезаписью (if_exists='replace')
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='replace',  # перезаписывает таблицу
        index=False,          # не сохраняет индекс DataFrame
        method='multi'        # ускоряет вставку для больших данных
    )
    
    print(f"DataFrame успешно сохранен в таблицу '{table_name}'")