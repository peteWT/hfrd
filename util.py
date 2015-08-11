from sqlalchemy import create_engine as ce


def eng(dbname='hfrd'):
    engine = ce('postgresql:///{0}'.format(dbname), echo=True)
    return engine
