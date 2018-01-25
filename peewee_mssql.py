from peewee import Database, ImproperlyConfigured, OP, QueryCompiler, CompoundSelect, SQL, Clause, CommaClause
from playhouse.db_url import register_database

__version__ = "0.1.3"

try:
    import pymssql
except ImportError:
    pymssql = None

try:
    from playhouse.pool import PooledDatabase
except ImportError:
    PooledDatabase = None

class MssqlQueryCompiler(QueryCompiler):
    # TODO: implement limit and offset properly, we can use:
    # SELECT *
    # FROM (SELECT ROW_NUMBER() OVER(ORDER BY id) RowNr, id FROM tbl) t
    # WHERE RowNr BETWEEN 10 AND 20

    def generate_select(self, query, alias_map=None):
        model = query.model_class
        db = model._meta.database

        alias_map = self.calculate_alias_map(query, alias_map)

        if isinstance(query, CompoundSelect):
            clauses = [_StripParens(query)]
        else:
            if not query._distinct:
                clauses = [SQL('SELECT')]
            else:
                clauses = [SQL('SELECT DISTINCT')]
                if query._distinct not in (True, False):
                    clauses += [SQL('ON'), EnclosedClause(*query._distinct)]

            # basic support for query limit
            if query._limit is not None or (query._offset and db.limit_max):
                limit = query._limit if query._limit is not None else db.limit_max
                clauses.append(SQL('TOP %s' % limit))

            select_clause = Clause(*query._select)
            select_clause.glue = ', '

            clauses.extend((select_clause, SQL('FROM')))
            if query._from is None:
                clauses.append(model.as_entity().alias(alias_map[model]))
            else:
                clauses.append(CommaClause(*query._from))

        if query._windows is not None:
            clauses.append(SQL('WINDOW'))
            clauses.append(CommaClause(*[
                Clause(
                    SQL(window._alias),
                    SQL('AS'),
                    window.__sql__())
                for window in query._windows]))

        join_clauses = self.generate_joins(query._joins, model, alias_map)
        if join_clauses:
            clauses.extend(join_clauses)

        if query._where is not None:
            clauses.extend([SQL('WHERE'), query._where])

        if query._group_by:
            clauses.extend([SQL('GROUP BY'), CommaClause(*query._group_by)])

        if query._having:
            clauses.extend([SQL('HAVING'), query._having])

        if query._order_by:
            clauses.extend([SQL('ORDER BY'), CommaClause(*query._order_by)])

        # NO OFFSET SUPPORT

        if query._for_update:
            for_update, no_wait = query._for_update
            if for_update:
                stmt = 'FOR UPDATE NOWAIT' if no_wait else 'FOR UPDATE'
                clauses.append(SQL(stmt))

        return self.build_query(clauses, alias_map)

class MssqlDatabase(Database):
    compiler_class = MssqlQueryCompiler
    commit_select = False
    interpolation = '%s'
    quote_char = '"'

    field_overrides = {
        'bool': 'tinyint',
        'double': 'float(53)',
        'float': 'float',
        'int': 'int',
        'string': 'nvarchar',
        'fixed_char': 'nchar',
        'text': 'nvarchar(max)',
        'blob': 'varbinary',
        'uuid': 'nchar(40)',
        'primary_key': 'int identity',
        'datetime': 'datetime2',
        'date': 'date',
        'time': 'time',
    }

    op_overrides = {
        OP.LIKE: 'LIKE BINARY',
        OP.ILIKE: 'LIKE',
    }

    def _connect(self, database, **kwargs):
        if not pymssql:
            raise ImproperlyConfigured('pymssql must be installed')

        if kwargs.pop('use_legacy_datetime', False):
            self.field_overrides['datetime'] = 'datetime'
            self.field_overrides['date'] = 'nvarchar(15)'
            self.field_overrides['time'] = 'nvarchar(10)'

        return pymssql.connect(database=database, **kwargs)

    def get_tables(self, schema=None):
        # should I not be using sys.tables?
        if schema:
            query = ('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE '
                     'TABLE_SCHEMA = %s AND TABLE_TYPE = %s ORDER BY TABLE_NAME')
            cursor = self.execute_sql(query, (schema, 'BASE TABLE',),
                                      require_commit=False)
        else:
            query = ('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE '
                     'TABLE_TYPE = %s ORDER BY TABLE_NAME')
            cursor = self.execute_sql(query, ('BASE TABLE',),
                                      require_commit=False)

        return [row[0] for row in cursor.fetchall()]

    def execute_sql(self, sql, params, *args, **kwargs):
        # convert params to tuple
        params = tuple(params)

        return super(MssqlDatabase, self).execute_sql(sql, params, *args, **kwargs)

register_database(MssqlDatabase, 'mssql')

if PooledDatabase:
    class PooledMssqlDatabase(PooledDatabase, MssqlDatabase):
        pass # TODO: implement _is_closed()

    register_database(PooledMssqlDatabase, 'mssql+pool')
