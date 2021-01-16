from pony import orm

refuge_db = orm.Database("sqlite", "refuge_testing.sqlite", create_db=True)
